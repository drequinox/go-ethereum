# Institutional Digital Asset Custody Platform
## Complete Design & Architecture Document

**Document reference:** CUSTODY-ARCH-001
**Status:** Reference architecture
**Audience:** Architecture review, security engineering, leadership, external auditors
**Working codename:** *Sentinel-Custody* (placeholder; align to programme naming as required)

---

## Table of contents

1. Executive summary
2. Design thesis and first principles
3. Requirements
4. Architectural overview
5. Trust model and the control-plane / data-plane split
6. The signing path — the security spine
7. Domain invariants (I-1 … I-12)
8. The Custody Abstraction Layer (CAL)
9. Cryptography and key management
10. The policy engine
11. The intelligence layer (AI, simulation, threat intelligence)
12. Conditional authorization and programmable settlement
13. Asset model — RWAs, permissioned tokens, account abstraction
14. Verifiability — transparency, proofs, selective disclosure
15. Recovery and resilience
16. Data model
17. API surface
18. Multi-institution and consortium custody
19. Compliance architecture
20. Scale, performance, and reliability
21. Consolidated threat model
22. Trade-offs and open questions
23. Build sequence and roadmap
24. Appendix A — invariant reference
25. Appendix B — glossary

---

## 1. Executive summary

This document specifies a complete reference architecture for an institutional-grade digital asset custody platform. It is designed to reach functional parity with the mature incumbent model — Wallet-as-a-Service built on MPC/TSS Network-Hosted-Keys, passkey request-signing, a programmable policy engine, and a multi-backend orchestration layer spanning MPC, HSM, and TEE — and then to surpass it on the dimensions that determine institutional procurement decisions in a post-Bybit market.

The architecture is organised around a single security spine: a signing path in which the bytes a human approves are cryptographically bound to the bytes that are signed, and in which no signature can be produced without a verifiable authorization token that the signing parties check independently, inside their own trust boundary, before contributing a share. We call these properties **What-You-See-Is-What-You-Sign (WYSIWYS) payload binding** and **token-gated signing**. Together they close the two structural gaps that the prevailing request-signing model leaves open: the *intent gap* (the human approves one thing while a different thing is signed) and the *trusted-orchestrator gap* (policy is bypassed when the service that calls the signer is compromised).

Around that spine we build a hexagonal **Custody Abstraction Layer (CAL)** that renders every cryptographic backend, chain, and compliance regime a swappable adapter rather than an architectural commitment. This is the property that lets one platform serve a startup running MPC-in-the-cloud and a regulated bank running its own HSMs inside its own compliance perimeter — without forking the codebase or weakening the invariants.

The document treats future-proofing not as a feature wishlist but as a discipline of cutting the right *seams* into the architecture today, so that capabilities we cannot yet build — post-quantum threshold signing, AI-enriched policy, tokenized real-world asset servicing, zero-knowledge proofs of compliance — arrive later as new adapters behind stable interfaces rather than as re-architectures. Every forward-looking capability in this document is additive to the deterministic, verifiable signing spine and never a replacement for it. That constraint is the single most important design decision in the platform.

---

## 2. Design thesis and first principles

We begin from a deliberately uncomfortable observation: the dominant custody architecture is cryptographically strong at the layer everyone inspects — the threshold signature — and structurally weak at the two layers nobody photographs. A platform can hold an unimpeachable MPC implementation and still lose a billion and a half dollars, because the catastrophic failures of 2025 were not breaks of the signing mathematics. They were breaks of the *binding* between human intention and machine action, and breaks of the *assumption* that the service orchestrating the signer is honest.

Five principles follow, and the rest of the architecture is their consequence.

**Principle 1 — The signed bytes are the approved bytes.** There must exist no point in the signing path at which the representation a human authorises diverges from the payload a signing party commits to. This binding must be enforced cryptographically, inside the trust boundary, not asserted by a user interface or a parsing service outside it.

**Principle 2 — Policy is a cryptographic precondition, not an advisory gate.** A signing party must refuse to contribute its share unless presented with a verifiable proof that policy admitted this exact payload. Compromising every service in front of the signer must not yield a signature.

**Principle 3 — Determinism is non-negotiable for anything that decides.** Any component whose output authorises value movement must be deterministic and replayable from an append-only log. Intelligence may *inform* a decision, but it may never *be* the decision, because a decision that cannot be replayed cannot be audited, certified, or defended to a regulator.

**Principle 4 — Vendor neutrality is structural.** No cryptographic protocol, HSM vendor, chain, cloud, or attestation format may be load-bearing in the domain core. Each is an adapter. Cryptographic agility — the ability to migrate protocols and primitives as research and regulation move — is a property we build now, not a promise we make later.

**Principle 5 — The operator is not a trusted party for the client's keys.** The strongest institutional guarantee is the one where the platform operator, acting alone, cannot reconstruct, move, or recover a client's assets. We design for client-sovereign recovery and, ultimately, for cross-institutional key-groups in which no single organisation holds a quorum.

Everything that follows — the plane split, the token-gated signing path, the CAL, the simulation layer, the proof systems — exists to make these five principles simultaneously true at institutional scale.

---

## 3. Requirements

### 3.1 Functional requirements

The platform creates and manages digital asset wallets at the scale of millions, across the three signature schemes that cover essentially the entire chain universe: ECDSA over secp256k1, EdDSA over Ed25519, and Schnorr over secp256k1 (BIP-340, Taproot). It performs threshold signing such that at no moment does a complete private key exist in cleartext, in memory, or at rest, at any node. It enforces a programmable, deterministic policy engine supporting amount thresholds, velocity windows, destination allow- and deny-lists, time windows, quorum requirements, and semantic call-data rules, governed by role- and attribute-based access control.

It renders every authorisation as a decoded, human-readable statement of transaction intent, and it binds that statement cryptographically to the payload that is signed. It manages the full key lifecycle — distributed key generation, proactive share refresh, share repair, and key rotation — without ever changing a wallet's public key or on-chain address. It provides three independent recovery rails. It maintains an append-only, tamper-evident, externally verifiable record of every authorisation and every signature. And it exposes a developer surface of REST APIs, webhooks, and typed SDKs, supporting delegated signing and tenant-isolated sub-organisations.

### 3.2 Non-functional requirements

| Dimension | Target | Incumbent reference |
|---|---|---|
| ECDSA signing throughput | ≥ 50 sig/s per key-group, horizontally scalable across key-groups | ~10 sig/s |
| EdDSA / Schnorr throughput | ≥ 200 sig/s | higher than ECDSA |
| Distributed keygen | ≥ 100 keygens/s | hundreds/s |
| Warm signing latency | p99 < 800 ms including policy evaluation, simulation, and WYSIWYS verification | — |
| Control-plane availability | 99.99% | continuous availability |
| Signing availability | survives loss of any single party, availability zone, or region | multi-site |
| Share durability | no key loss under loss of `t−1` parties; operator, geographic, and cloud diversity | T3+/4 sites |
| Compliance | SOC 2 Type II, ISO 27001, DORA, MiCA CASP, GDPR; FIPS 140-3 Level 3 in HSM mode | SOC 2 Type II, GDPR |

### 3.3 Constraints

Vendor neutrality is mandatory: the platform runs on multiple MPC libraries and multiple HSM vendors behind one abstraction, with no protocol lock-in. Regulated-institution deployment is a native mode, not a bolt-on: the platform must support on-premises, client-VPC, and "keys never leave my compliance perimeter" topologies as first-class deployment patterns. Cryptographic agility is structural: protocol and curve choices must be swappable as threshold-signature research advances, without re-architecting the platform.

---

## 4. Architectural overview

The platform divides into two planes whose separation is the foundation of the entire trust model, and a set of cross-cutting services that span both.

```
                    ┌────────────────────── CONTROL PLANE (untrusted, internet-facing) ──────────────────────┐
   client / SDK ──► │  API Gateway → AuthN (WebAuthn / passkey request-signing)                                │
                    │       │                                                                                  │
                    │       ▼                                                                                  │
                    │   Orchestrator ──► Intent Decoder ──► Transaction Simulator ──► Risk/Intel Enrichment    │
                    │       │                 │                    │                        │                  │
                    │       │                 └────────► CanonicalIntent + payloadDigest + enrichmentSnapshot  │
                    │       ▼                                                                                  │
                    │   Policy Engine (deterministic) ──► Authorization Service ──► PolicyDecisionToken         │
                    │       │                                       (signed by enclave-held decision key)       │
                    │       ▼                                                                                  │
                    │   Transparency Log (append-only · Merkle · externally witnessed · proof-serving)         │
                    └───────┼──────────────────────────────────────────────────────────────────────────────────┘
                            │  signed signing-request: { payloadDigest, rawTxPreimage, PolicyDecisionToken,
                            │                            conditionProofs[], attestationRequirements }
                            ▼
   ┌──────────────────── DATA PLANE (trusted · attested · no inbound internet) ─────────────────────────────────┐
   │   Custody Abstraction Layer (CAL) — hexagonal, domain core depends only on SPI ports                       │
   │                                                                                                            │
   │   AuthorisationVerifier.Admit()  ── verifies token, freshness, WYSIWYS digest, quorum & condition proofs   │
   │            │  (enforced INSIDE each signing party's enclave, before any share is touched)                  │
   │            ▼                                                                                                │
   │   SigningPort ─┬─► CGGMP21 MPC cluster   ─┐                                                                 │
   │                ├─► DKLS23 MPC cluster      │  each party in an attested TEE; shares never centralised       │
   │                ├─► FROST MPC cluster       │                                                                │
   │                ├─► PKCS#11 HSM backend     │  (Thales · IBM Crypto Express · Entrust · nCipher)            │
   │                └─► TEE single-sig backend ─┘  (constrained hot-path / low-value only)                       │
   │                                                                                                            │
   │   KeyLifecyclePort · AccountPort · PolicyEnforcementPort · AttestationPort · TransportPort · ConditionPort │
   └────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The control plane is stateless, horizontally scaled, internet-facing, and holds no key material whatsoever. It may be entirely compromised without yielding a signature, because the data plane re-verifies every authorisation cryptographically. The data plane is network-isolated with no inbound internet path, attestable end-to-end, and is the only location in the system where key shares exist. The Custody Abstraction Layer is the hexagonal core of the data plane: its domain logic depends only on a set of service-provider-interface (SPI) ports, and every cryptographic backend, chain adapter, and attestation mechanism plugs in behind one of them.

The cross-cutting services — the transparency log, the attestation infrastructure, the key-management ceremonies, and the observability stack — span both planes but are designed so that their *control-plane* components are advisory and their *data-plane* components are authoritative. Where a service must be trusted, it lives in the data plane; where it can be untrusted-but-verified, it lives in the control plane and its outputs are checked downstream.

---

## 5. Trust model and the control-plane / data-plane split

The defining inversion of this architecture, relative to the prevailing model, is that **the data plane does not trust the control plane.** In the request-signing model, the policy engine sits in front of the signer and the signer signs whatever the orchestrator hands it; the security of the system therefore rests on the integrity of every service between the user and the signing parties. We reject that. Here, the signing parties treat the control plane as an untrusted source of *requests* and an untrusted source of *proposed payloads*, and they independently verify that policy admitted the precise bytes in front of them before they will act.

This has a concrete and load-bearing consequence. An adversary who achieves complete control of the orchestrator, the policy-engine host, the API gateway, and the intent decoder — every service in the control plane — still cannot extract a signature, because they cannot forge a `PolicyDecisionToken` (it is signed by a key held only inside the data plane's attested enclaves) and they cannot make a swapped payload pass the WYSIWYS digest check (it is verified inside the signing party against the digest the human approved). The control plane is, by design, a convenience and a user experience; it is not a trust anchor.

The trust anchors are three, and only three. First, the attested enclaves that host the signing parties, whose measurements are verified before a party is admitted to a key-group and re-verified before each signing operation. Second, the threshold distribution itself, which ensures that compromising fewer than `t` parties yields nothing. Third, the externally-witnessed transparency log, which ensures the operator cannot rewrite history to conceal an unauthorised action. We deliberately spread trust across these three so that the failure of any one does not collapse the system: a side-channel break of the enclave is contained by the threshold; a threshold compromise is detected and bounded by the log; a log compromise is caught by external witnesses.


---

## 6. The signing path — the security spine

This is the component on which the platform succeeds or fails. We specify it as an ordered sequence in which every transition enforces an invariant. The path is the same regardless of which signing backend ultimately produces the signature, because the CAL presents a uniform contract.

```
 1. Submit intent          client → { walletId, chain, unsigned-tx OR structured-intent }
 2. Canonicalise           Intent Decoder → CanonicalIntent { from, to, asset, amount,
                             decoded-calldata, chainId, nonce } and
                             payloadDigest = H(deterministic-serialisation(payload))
 3. Simulate               Transaction Simulator forks chain at current state, executes,
                             produces stateDiff { balance moves, allowance grants, ownership
                             changes } and simDigest = H(stateDiff)
 4. Enrich                 Risk/Intel Enrichment snapshots risk score, threat-intel matches,
                             sanctions/eligibility results → enrichmentSnapshot + snapshotHash
 5. Render WYSIWYS         human-readable approval object derived ONLY from the payloadDigest
                             preimage and the stateDiff — never from a free-form UI string
 6. Approve               approver passkey signs over (payloadDigest ‖ simDigest ‖
                             approvalContextHash) — binds human consent to bytes AND outcome
 7. Evaluate policy        Policy Engine: deterministic decision over CanonicalIntent +
                             enrichmentSnapshot + signer identities → admit / deny / require-quorum
 8. Issue token           Authorization Service →
                             PolicyDecisionToken = Sign_decisionKey({ payloadDigest, simDigest,
                               walletId, policyVersion, snapshotHash, quorumProof,
                               conditionRefs[], notBefore, notAfter, decisionId })
 9. Request signature      CAL.SigningPort.sign({ payloadDigest, rawTxPreimage,
                             PolicyDecisionToken, conditionProofs[] })
10. Admit (in enclave)     AuthorisationVerifier.Admit() inside EACH signing party:
                             • verify token signature against pinned decision-key public half
                             • verify notBefore ≤ now ≤ notAfter and decisionId unused
                             • verify H(rawTxPreimage) == payloadDigest == token.payloadDigest
                             • verify quorumProof and all conditionProofs[]
                             • REFUSE on ANY mismatch
11. Sign                   t parties run the threshold protocol; share never leaves enclave
12. Assemble               signature returned with attestation { decisionId, parties,
                             enclave measurements, protocol }
13. Log                    Transparency Log appends tamper-evident entry; broadcast permitted
                             only after an inclusion proof is obtained
```

Three guarantees emerge from this path that the request-signing model cannot provide.

The first is **intent integrity**, which closes the Bybit/Lazarus class directly. The bytes signed at step 11 are bit-identical to the digest the human approved at step 6, because step 10 verifies `H(rawTxPreimage) == payloadDigest == token.payloadDigest` inside the trust boundary. A malicious orchestrator that swaps `rawTxPreimage` after approval fails this check at every honest party, and since fewer than `t` parties cannot sign, the swap cannot succeed. Crucially, the human also approved the *simulated outcome* (`simDigest`), so even a semantically valid but malicious payload — an `approve(unlimited)` to an attacker, a `setOwner` masquerade — is one the human consciously authorised against a rendered state diff, not a decoded blob they could not interpret.

The second is **policy non-bypass**. There is no signature without a `PolicyDecisionToken`, and the token is verified independently by each signing party against a decision-key public half that is pinned inside the enclave at provisioning time. Compromising the policy-engine host does not let an adversary forge the token, because the signing key for the token lives in the data plane, not in the policy host. Policy ceases to be a gate one can route around and becomes a precondition baked into the cryptographic protocol.

The third is **replay and staleness resistance**. The token carries `notBefore`, `notAfter`, and a single-use `decisionId`, all bound into the payload digest. A captured token cannot be replayed against a different payload (the digest will not match) nor reused for the same payload after expiry (the `notAfter` check fails) nor used twice (the `decisionId` is consumed).

A critical implementation note governs the whole path: `AuthorisationVerifier.Admit()` runs *inside each signing party's enclave*, not in a shared gatekeeper service in front of the cluster. This is the difference between "policy is checked" and "policy cannot be skipped." A shared gatekeeper is itself a single point one can compromise or bypass; per-party in-enclave verification means an adversary must defeat the admission logic in `t` independent attested environments simultaneously, which is precisely the threshold assumption the whole system already rests on.

---

## 7. Domain invariants (I-1 … I-12)

The CAL domain core enforces a fixed set of invariants regardless of which backend, chain, or compliance regime is active. These are the contract; adapters may not violate them, and the core rejects any operation that would. The first eight are the security and correctness spine; I-9 through I-12 extend the spine to cover the forward-looking capabilities and are written so that they can be enforced from day one even where the corresponding feature ships later.

| ID | Invariant | Enforcement point |
|---|---|---|
| **I-1** | No complete private key ever exists in cleartext at any node, at any time | KeyLifecyclePort; all SigningPort backends |
| **I-2** | WYSIWYS payload binding: signed bytes ≡ approved bytes ≡ token bytes | AuthorisationVerifier.Admit(), in-enclave |
| **I-3** | No signature without a valid, fresh, single-use PolicyDecisionToken | AuthorisationVerifier.Admit(), per-party |
| **I-4** | Every policy decision is deterministic and replayable from the log | Policy Engine; Transparency Log |
| **I-5** | Every signing party runs in an attested enclave verified before admission | AttestationPort |
| **I-6** | Key lifecycle operations never change the public key / address | KeyLifecyclePort |
| **I-7** | The operator alone cannot reconstruct a client's keys | Recovery rails; key-group membership model |
| **I-8** | History is append-only and externally verifiable | Transparency Log + external witnesses |
| **I-9** | Intelligence (AI/ML) output is a signed input to policy, never the decision | Enrichment service; Policy Engine |
| **I-10** | Conditional authorizations release only on cryptographically proven conditions | ConditionPort; AuthorisationVerifier |
| **I-11** | Asset-level transfer restrictions are honoured before authorization | AccountPort; Policy Engine |
| **I-12** | Every sensitive record supports authorised selective disclosure | Data model; encryption layer |

The load-bearing invariant is **I-2**. Everything else protects, extends, or audits the binding it guarantees. When evaluating any proposed feature or adapter, the first question is always whether it preserves I-2; if it cannot, it does not enter the platform in that form.


---

## 8. The Custody Abstraction Layer (CAL)

The CAL is the orchestration moat and the structural answer to vendor lock-in. It is a hexagonal (ports-and-adapters) architecture in which the custody domain core — the entity that knows about wallets, key-groups, policies, invariants, and the signing path — depends only on a set of service-provider interfaces. Every concrete technology sits behind a port as an adapter, and the core neither knows nor cares which adapter is wired in.

### 8.1 The SPI ports

| Port | Responsibility | Representative adapters |
|---|---|---|
| `SigningPort` | Produce a signature for a payloadDigest under a key-group | CGGMP21-MPC, DKLS23-MPC, FROST-MPC, PKCS#11-HSM, TEE-single |
| `KeyLifecyclePort` | DKG, proactive refresh, share repair, rotation, derivation | per-protocol implementations |
| `AccountPort` | Address derivation, chain account model, transfer-restriction semantics | per-chain adapters; permissioned-token adapters |
| `PolicyEnforcementPort` | Evaluate canonical intent and issue the decision token | deterministic policy engine |
| `AttestationPort` | Verify enclave / HSM attestation evidence | AWS Nitro, Intel TDX, AMD SEV-SNP, PKCS#11 KAT |
| `TransportPort` | Inter-party communication and chain broadcast | gRPC over mTLS; per-chain RPC |
| `ConditionPort` | Evaluate and prove external release conditions | oracle adapters, HTLC verifiers, DvP settlement proofs |

A new HSM vendor is a new `SigningPort` + `AttestationPort` adapter. A new chain is a new `AccountPort` + `TransportPort` adapter. A new threshold protocol is a new `SigningPort` + `KeyLifecyclePort` adapter. In every case the signing path, the invariants, and the domain core do not move. This is the property that lets one platform run the *identical* custody logic in three radically different deployment modes — MPC in the operator's cloud, the client's own Thales or IBM HSMs inside the client's VPC, or a hybrid of both — and present a single API, a single policy model, and a single audit surface across all of them.

### 8.2 Why the abstraction must be cleaner than the incumbent's

The incumbent is moving toward this same orchestration position, retrofitting an HSM service onto an MPC-first platform. Retrofit abstractions leak: the original protocol's assumptions bleed into the interface, and the "abstraction" ends up shaped like the first backend it wrapped. We avoid this by deriving the port contracts from the *invariants*, not from any backend. `SigningPort` does not expose "MPC rounds" or "HSM sessions"; it exposes "produce a signature for this digest under this key-group, having satisfied Admit()." That contract is equally honest whether fulfilled by a five-party CGGMP21 protocol or a single PKCS#11 call to a hardware module. The abstraction is clean because it was designed before the backends, against the invariants the backends must serve.

---

## 9. Cryptography and key management

### 9.1 Protocol selection

| Scheme / curve | Protocol | Rationale |
|---|---|---|
| ECDSA secp256k1 (default) | **CGGMP21** | Identifiable abort — a cheating party is named, not merely detected — which is the direct structural fix for the GG18/GG20 (TSSHOCK) extraction class. GG20 is banned from production. |
| ECDSA secp256k1 (throughput tier) | **DKLS23** | OT-based, two-round online; high throughput for EVM hot paths where identifiable abort can be traded for speed under tighter monitoring. |
| EdDSA Ed25519 | **FROST** | Round-optimised threshold Schnorr; additive nonce shares; substantially higher throughput than threshold ECDSA. |
| Schnorr / Taproot (BIP-340) | **FROST** | Native key-path Taproot spend support, awkward or impossible in a GG-only stack. |

Protocol choice is a property of the **key-group**, fixed at DKG time and recorded in metadata. The `SigningPort` dispatches on it. This is what makes cryptographic agility structural: migrating a key from CGGMP21 to a future post-quantum threshold scheme is a *re-share* operation under `KeyLifecyclePort`, not a re-architecture, and it leaves the public key and on-chain address unchanged (I-6).

### 9.2 Cryptographic agility as a first-class property

Every primitive in the platform is versioned and negotiated, never hard-coded: the signing scheme, the hash function, the transport cipher suite, the attestation format, and the signature algorithm of the `PolicyDecisionToken` itself. Each carries a version tag in the metadata of the object it protects, and each has a defined migration path. The discipline is absolute because the failure mode it guards against is existential: the day a primitive is broken, migration must be a configuration-and-reshare exercise, never a platform rebuild. We treat "which hash, which curve, which cipher" as runtime-negotiated facts about a key-group or a session, not as compile-time constants.

### 9.3 Share storage and trust distribution

Key shares are held under a `t-of-n` threshold with operator, geographic, and cloud-provider diversity, and that diversity is *policy-declared and attested* rather than merely claimed. Each party runs inside a TEE — AWS Nitro Enclaves, Intel TDX, or AMD SEV-SNP — whose attestation is verified through `AttestationPort` before the party is admitted to a key-group, and re-verified before each signing operation (I-5). We deliberately treat the enclave as one defensive layer rather than the trust root, because TEEs have a poor side-channel history; the threshold distribution and the transparency log are the other two layers, and the design ensures no single layer's failure is catastrophic.

Proactive secret sharing refreshes shares on a fixed cadence and on heuristic triggers — anomaly detection, party rotation, post-incident — producing new shares that are *verifiably consistent* with the unchanged public key, via a publicly checkable transcript. Refresh and repair never expose the secret and never alter the address (I-6). Share repair, in which a lost party reconstructs its share from `t` others, is itself gated behind the `PolicyDecisionToken` machinery and logged, so that the recovery machinery cannot become a covert extraction path.

### 9.4 Post-quantum posture

No production-ready threshold-lattice signature scheme exists as of this writing, so we do not build one; we build the ability to *adopt* one and we hedge the parts we can today. The harvest-now-decrypt-later threat does not bear on secp256k1 signatures in the near term, but it bears immediately on *transport confidentiality* and *backup confidentiality* — an adversary recording today can decrypt later. We therefore deploy post-quantum protection on the transport channel and on cold backups now, using hybrid classical-plus-ML-KEM key establishment, while keeping the signing-scheme migration seam clean for when a vetted threshold-PQ signature scheme and NIST threshold guidance exist. Keygen metadata carries a `migrationPath` field from day one.


---

## 10. The policy engine

The policy engine is deterministic, versioned, and — the property that distinguishes it from an advisory gate — its output is a *signed artifact* rather than a side effect. A policy evaluation does not "let the request through"; it produces a `PolicyDecisionToken` that the signing parties subsequently verify, and absent that token there is no signature (I-3).

### 10.1 Rule classes

The engine supports amount thresholds; rolling velocity windows; destination allow- and deny-lists keyed on on-chain address, ENS or chain-native name, and travel-rule VASP identifier; per-asset and per-chain rules; time-of-day and day-of-week windows; quorum requirements expressed as M-of-N over a named approver set; attribute- and role-based access control over who may even initiate; and — the class that matters most — *semantic call-data rules*. The last evaluates the decoded meaning of a transaction, not its surface form, so that a rule such as "an `approve()` granting unlimited allowance to a non-allowlisted spender is denied" can be expressed and enforced. This is the rule class that would have caught the Bybit manipulation at the policy layer even before WYSIWYS binding caught it at the signing layer — a defence in depth that is deliberate.

### 10.2 Determinism

Policy evaluation is a pure function of the canonical intent, the policy version, the enrichment snapshot, and the approver set. The same inputs always yield the same decision, and the decision is replayable from the transparency log (I-4). To preserve this, evaluation performs no network calls: all enrichment — price feeds, sanctions lists, threat intelligence, risk scores — is *snapshotted into the intent before evaluation*, and the snapshot's hash is bound into the signed decision. A regulator asking why a particular forty-million-dollar transfer was approved on a particular date can be answered definitively by replaying that policy version against the logged canonical intent and enrichment snapshot, and obtaining a bit-identical decision. A policy engine that makes live calls during evaluation cannot make this guarantee, and so we forbid it.

### 10.3 Versioning and provenance

Policy sets are versioned, and every decision records the exact `policyVersion` that produced it. The decision token is signed by an enclave-held decision key whose public half is pinned in every signing party. Decision provenance is therefore independently and permanently verifiable: one can prove, years later, that a given signature was issued under a given policy version against a given intent, without trusting the operator's word for it.

---

## 11. The intelligence layer (AI, simulation, threat intelligence)

This is where "AI-enhanced custody" is made real *without* breaking the determinism the platform depends on. The governing rule is I-9: **intelligence is a signed input to a deterministic decision, never the decision itself.** A model that *is* the approver is non-replayable, uncertifiable, and indefensible to a regulator who asks why a transfer was authorised; "the model assessed it as low-risk" is not an audit answer. So every intelligence capability below produces an output that is snapshotted, hashed, bound into the canonical intent, and consumed by the deterministic policy engine as data — and the decision remains a pure, replayable function of those data.

### 11.1 Transaction simulation as a custody primitive

The single highest-leverage capability in this layer, and arguably in the platform, is full-state transaction simulation. Before approval, the simulator forks the relevant chain at current state, executes the proposed transaction, and produces the *actual resulting state diff* — which balances move, which allowances are granted, which ownership or admin rights change — rather than a decode of the call-data. This is the strongest possible form of WYSIWYS: the human approves an *outcome*, not a payload they cannot interpret. It catches the entire `approve(unlimited)` / `setOwner` / delegatecall-manipulation class semantically, because the malicious effect appears in the state diff regardless of how the call-data is obfuscated. The simulation result is hashed into `simDigest` and bound into the approver's signature (step 6 of the signing path) and into the decision token, so the outcome the human saw is cryptographically tied to the bytes that get signed.

### 11.2 AI as signed advisory enrichment

Within the I-9 frame, the genuinely valuable model-driven capabilities are: anomaly detection over signing patterns, flagging deviations from an approver's or wallet's established behaviour (an approver who never signs at 03:00 to a freshly-created address); intent-decoding assistance for novel or proxy contracts where static decoders fail, improving the WYSIWYS render for the long tail; natural-language summarisation of the simulated state diff into the approval object; and correlation against threat intelligence. Each of these produces a score or a classification that becomes a signed snapshot feeding the deterministic engine. The engine then expresses human-authored rules over those signals — "if model-risk-score exceeds X and amount exceeds Y and destination is not allowlisted, escalate to a 3-of-5 quorum or deny." The intelligence sharpens the inputs; the rule, written and versioned by humans, makes the decision.

### 11.3 Live threat-intelligence-driven policy

Custody policy consumes a real-time feed of known-bad addresses, sanctioned entities, freshly-flagged exploit contracts, and bridge-compromise signatures — the typed, structured intelligence that a dedicated threat-intelligence pipeline produces and exports in a standard schema. The seam is a `PolicyEnrichmentPort` that snapshots the current threat state into the intent before evaluation, preserving determinism. The strategic differentiator is reaction time: custody that incorporates new threat intelligence within minutes, rather than at the next policy redeploy, materially shrinks the window in which a freshly-weaponised address or contract can be transacted with. For an institution, "we stopped transacting with that address eight minutes after it was flagged" is a meaningfully different risk posture from "we updated our deny-list in next week's release."

---

## 12. Conditional authorization and programmable settlement

The `PolicyDecisionToken` already proves "policy said yes." We generalise it so that a token can additionally encode "and *these* conditions are cryptographically proven true," and the `AuthorisationVerifier` will not admit the signature until the `conditionProofs[]` it carries satisfy the `conditionRefs[]` the token names (I-10). This single generalisation is the foundation for an entire class of institutional settlement products.

With conditional authorization in place, the platform supports atomic delivery-versus-payment, in which the asset leg signs only when proof of the payment leg is presented; escrow and milestone release, in which signing is gated on an attested external event; time-locked and condition-locked release, including hashed-timelock contracts for cross-chain atomic swaps; and multi-leg settlement, in which a basket of signatures is admitted together or not at all. The architectural elegance is that none of these is a special case in the signing path — each is a different population of the `conditionRefs[]` and `conditionProofs[]` fields, evaluated through the `ConditionPort`, against the same `Admit()` gate that already enforces policy and WYSIWYS. We build one mechanism and unlock a product line.

---

## 13. Asset model — RWAs, permissioned tokens, account abstraction

Institutional custody is moving off plain externally-owned accounts holding bearer assets toward tokenized deposits, money-market funds, and securities issued under permissioned standards that carry transfer restrictions, on-chain identity gating, and issuer-controlled rules. An account model that assumes unrestricted bearer assets cannot custody the assets institutions are about to issue. We therefore make three structural commitments in the `AccountPort` now.

First, **permissioned-token semantics are native**. The account model understands that a transfer can be rejected by the *asset itself*, that holder eligibility may be a precondition, and that the holder is not free to send anywhere. This is enforced as invariant I-11: asset-level transfer restrictions are evaluated before authorization, so the platform never produces a signature for a transfer the token will reject on-chain, and never presents an approver with an intent that is invalid at the asset layer.

Second, **asset servicing is a seam, not an afterthought**. Tokenized securities have lifecycles — coupons, redemptions, corporate actions, voting, rebasing — and custody platforms become asset-servicing platforms over time. We do not build the full servicing engine now, but the data model carries an asset-lifecycle seam so that a held position can have events acted upon it under policy. A platform that is only a keystore competes poorly in a market that wants a custodian.

Third, **account abstraction is modelled, not ignored**. Modular smart accounts under ERC-4337 and ERC-7579, session keys, and intent-based execution are becoming the default account model. The `AccountPort` models "an account is a programmable contract with its own rules" alongside "an account is a keypair," so the platform can co-sign and reason about smart accounts — issuing session keys under policy, approving module installs, governing paymaster relationships — rather than only signing EOA transactions. Chain abstraction follows the same logic: adding a chain is an adapter and a configuration entry, and the forward bet is chain-abstracted addressing with intent-based cross-chain settlement, while bridges — the dominant hack vector in the ecosystem — sit behind a policy-governed, threat-intel-screened boundary rather than being implicitly trusted.

---

## 14. Verifiability — transparency, proofs, selective disclosure

### 14.1 The transparency log

Every authorisation and every signature is recorded in an append-only, Merkle-chained log that is periodically witnessed by an independent party and, optionally, anchored to a public chain (I-8). A signature is broadcast only after an inclusion proof is obtained, so that no signed transaction escapes the audit record. The log is the substrate for everything in this section, and it is what converts "trust the operator's database" into "verify the operator's history."

### 14.2 From trusted logs to verifiable proofs

The strategic trajectory is to move from "trust our append-only log" to "here is a proof you can verify yourself." Two proof systems are the targets. **Proof of reserves and solvency** lets the platform cryptographically demonstrate that it holds what it claims, without exposing every individual position. **Proof of policy compliance** lets the platform produce a zero-knowledge proof that a given signature was issued under a valid policy decision against a valid intent, verifiable by an auditor or a counterparty without revealing the policy internals or the transaction detail. The endgame is that a regulator becomes a *verifier* rather than an *investigator*, and audit cost collapses because evidence is mechanically checkable rather than manually reconstructed.

### 14.3 Selective disclosure

Institutions require confidentiality from the public and full transparency to auditors and regulators, and those are not contradictory if disclosure is built as a structured capability rather than an all-or-nothing switch. Invariant I-12 requires that every sensitive record support authorised selective disclosure — viewing-key or credential-gated access to specific records for specific parties. This is the same identity-and-eligibility rail that permissioned tokens demand, which is one reason to build it early. Retrofitting privacy into a system designed in the clear is close to impossible, so the disclosure seam exists from the schema upward even where the initial deployment stores records in the clear.

---

## 15. Recovery and resilience

### 15.1 Three independent recovery rails

We provide three recovery mechanisms and never collapse them into one, because each addresses a distinct failure mode and conflating them creates a single point of failure.

The **operational rail** handles party loss. Proactive secret sharing repairs a lost party's share from `t` others, fully automated and threshold-protected, with no human ever seeing key material. The **client-sovereign cold rail** handles catastrophic platform loss. A threshold-encrypted backup is held such that its *decryption* is itself an M-of-K ceremony controlled by the client's own officers, with their key shares wrapped in their own HSMs. The platform operator, acting alone, can never reconstruct it — which is the institutional dealbreaker and the concrete expression of invariant I-7. The **governance rail** handles human failure: lost or compromised approvers are recovered through a quorum reconfiguration governed by the organisation's admin multi-sig, gated behind a mandatory time-lock and out-of-band confirmation, which is where social-engineering and coercion attempts are caught.

### 15.2 Provable, continuous recoverability

Operational-resilience regulation increasingly requires that recovery be *demonstrated*, not asserted. We therefore make recovery a first-class, continuously-exercised path rather than an emergency procedure discovered to be broken at the worst moment. Scheduled, automated recovery game-days exercise each rail and produce a cryptographic proof-of-recoverability as an audit artifact. The platform does not wait for a disaster to learn whether its recovery works.


---

## 16. Data model

The data model splits sharply along the trust boundary: relational storage for orchestration metadata that may live in the untrusted control plane, the transparency log for the verifiable audit record, and share storage that exists only inside the data-plane parties and is never centralised.

```
Organization 1─* SubOrg 1─* User
User *─* Credential        { type: passkey|did|vc, publicKey, requestSigningKey }
Organization 1─* Wallet
Wallet 1─1 KeyGroup        { protocol, curve, t, n, partySet[], publicKey, address,
                            migrationPath, diversityPolicy }
KeyGroup 1─* ShareRef      { partyId, attestationRef }   ← reference + attestation only; NEVER the share
Wallet 1─* PolicySet       (versioned)
Wallet 1─* AssetPosition   { assetType, restrictions[], lifecycleEvents[] }
SigningRequest            { id, walletId, canonicalIntent, payloadDigest, simDigest, status }
  ├─1 EnrichmentSnapshot  { riskScore, threatIntelMatches[], sanctions, eligibility, snapshotHash }
  ├─1 PolicyDecision      { decisionId, policyVersion, snapshotHash, quorumProof,
                            conditionRefs[], token, notBefore, notAfter }
  ├─* ConditionProof      { conditionRef, proof, verifiedAt }
  └─1 SignatureRecord     { sig, parties[], attestation, protocol, logInclusionProof }
TransparencyLogEntry      { seq, prevHash, entryHash, payload, witnessSignatures[] }
DisclosureGrant           { recordRef, grantee, viewingKey, scope, expiry }   ← I-12
```

The storage split follows three rules. Relational storage — organisations, users, wallets, key-group *metadata*, policy versions, request, decision, and signature records — may live in the control plane and holds no share material. The transparency log is append-only, Merkle-chained, and externally witnessed, and is authoritative for the audit history. Share storage lives only inside the data-plane signing parties; the relational layer holds attestation references and never the material itself, which is the data-model expression of invariant I-1.

---

## 17. API surface

The control plane exposes a request-signed REST API: every state-changing call carries a passkey signature over the request, which is the one element of the incumbent model we retain unchanged because it is correct. The API is complemented by webhooks for asynchronous lifecycle events, typed SDKs in TypeScript, Go, Python, and Rust, and a delegated-signing flow for end-user-embedded wallets in which the end user's passkey is the approver and the organisation is a co-signer in policy.

```
POST /wallets                          create wallet (triggers DKG)
GET  /wallets/{id}
POST /wallets/{id}/signatures          submit intent → returns pending authorization
GET  /signatures/{id}                  status + WYSIWYS intent + simulated stateDiff + attestation
POST /signatures/{id}/approve          approver passkey-signs (payloadDigest ‖ simDigest ‖ ctx)
POST /wallets/{id}/policies            attach / version a policy set
POST /keygroups/{id}/refresh           proactive share refresh
POST /keygroups/{id}/rotate            key rotation
POST /keygroups/{id}/migrate           protocol / primitive migration (re-share)
POST /recovery/operational             party repair
POST /recovery/cold                    initiate client-sovereign cold ceremony
POST /recovery/governance              quorum reconfiguration (time-locked)
POST /conditions/{ref}/prove           submit a condition proof for a pending signature
GET  /transparency/{seq}/proof         inclusion proof for external verification
POST /disclosure/grants                issue a selective-disclosure grant (I-12)
GET  /assets/{id}/restrictions         permissioned-token transfer restrictions
```

---

## 18. Multi-institution and consortium custody

The strongest form of invariant I-7 — that the operator alone cannot reconstruct a client's keys — is a key-group whose `n` parties span *different institutions* rather than one operator's diversified machines. The party-membership model therefore allows cross-organisational quorums from the outset: a key-group may be composed of parties contributed by the client, the custodian, and an independent recovery agent, such that no single organisation holds a quorum and collusion across organisational and jurisdictional boundaries would be required to act unilaterally. This is the foundation of consortium custody, collaborative-custody products, and the credible-neutrality story that wins the most conservative institutional clients. We build the membership model to support it now, even if early deployments use single-operator diversity, because retrofitting cross-institutional quorums into a single-operator party model is a structural change rather than a configuration.

---

## 19. Compliance architecture

SOC 2 Type II and GDPR are the floor. We differentiate on operational resilience and on making compliance itself a versioned, hot-loadable layer rather than a release-bound one.

Compliance rules — sanctions screening, travel-rule VASP resolution, eligibility and KYC gating, jurisdiction-specific transfer rules — are expressed as a *versioned, jurisdiction-scoped, hot-loadable* policy layer that updates without a platform redeploy and that records which ruleset version applied to each decision. This is policy-as-code for regulation, and it is how one platform operates across many regulatory regimes simultaneously: DORA's operational-resilience obligations are evidenced directly by the multi-region threshold posture and the tested, proof-producing recovery rails; MiCA CASP custody obligations are met by the segregation, the client-sovereign recovery, and the audit surface; FIPS 140-3 Level 3 is available in HSM-backed mode; and travel-rule integration is first-class, with VASP identifiers modelled as allowlist entities in the policy engine. The transparency log doubles as the compliance evidence engine — replayable decisions are mechanically auditable, which most competitors cannot offer and which converts a regulatory examination from an investigation into a verification.

---

## 20. Scale, performance, and reliability

The control plane is stateless behind the gateway and scales horizontally; policy evaluation is CPU-bound and pure, and therefore parallelises trivially. Signing throughput scales by sharding across independent key-groups and by protocol selection — DKLS23 and FROST serve hot paths where throughput dominates, CGGMP21 serves high-value paths where identifiable abort dominates. A single key-group is bounded by its protocol's round count, so platform-level throughput is a function of key-group count, which makes wallet sharding the primary scaling lever.

Signing availability derives from the threshold itself: with `n` parties spread across availability zones, regions, and operators, the loss of any single party — or an entire region — still leaves a signing quorum, a guarantee strictly stronger than any single-HSM or single-region design. Parties are treated as cattle rather than pets; a lost party is re-provisioned with fresh attestation and its share repaired through proactive secret sharing, so no standby key material sits idle as a latent liability.

Observability spans both planes: per-party attestation freshness, quorum health, policy-decision rate and deny-reason distribution, simulation-divergence alerts, transparency-log witness lag, and — the hardest alert in the system — any `Admit()` rejection. An admission rejection means either an active attack or a drift between the control and data planes, and both are incidents that page immediately.

---

## 21. Consolidated threat model

| Threat | Incumbent-model exposure | This architecture |
|---|---|---|
| Compromised orchestrator swaps payload after human approval | Real — request-signing binds the API request, not the broadcast bytes | Closed by I-2: `H(preimage) == payloadDigest` verified in-enclave |
| Semantically valid but malicious payload (approve-unlimited, setOwner) | Approver sees decoded call-data they may not interpret | Closed by simulation: approver signs over the rendered state diff (simDigest) |
| Policy bypass via compromised control-plane service | Plausible — policy gates, signer trusts caller | Closed by I-3: no token, no share contribution; verified per-party |
| TSS protocol-level key extraction (TSSHOCK / GG20) | Exposure if GG18/GG20 in use | Closed: CGGMP21 default with identifiable abort; GG20 banned |
| Single party / region compromise | Mitigated by threshold | Same — threshold plus attested party diversity |
| Operator reconstructs client keys from cold backup | Mitigated via auth-credential separation | Closed harder: client-sovereign M-of-K cold recovery; operator cannot decrypt (I-7) |
| History rewrite to conceal an unauthorised signature | Operator-trusted audit logs | Closed by I-8: externally-witnessed transparency log with inclusion proofs |
| Approver social-engineering or coercion | Policy and RBAC | Governance recovery rail with time-lock and out-of-band confirmation |
| AI/ML approves a malicious transaction | N/A or opaque if model-gated | Prevented by I-9: model output is signed input to deterministic policy, never the decision |
| Conditional / settlement leg released without counter-leg | N/A | Closed by I-10: ConditionPort proofs verified at Admit() |
| Transfer of a restricted asset to an ineligible holder | Depends on integration | Closed by I-11: asset restrictions evaluated before authorization |
| Harvest-now-decrypt-later against transport / backups | Exposure | Mitigated: hybrid PQ key establishment on transport and cold backups now |

The honest scorecard: on raw MPC engineering, chain breadth, and developer-experience polish, the incumbent is mature, and reaching parity there is a real and well-funded grind. The architectural advantage of this design is concentrated in the signing path (§6), the CAL (§8), the simulation-bound WYSIWYS (§11.1), and the verifiability layer (§14) — which is precisely where the regulated, post-Bybit institutional buyer actually makes the procurement decision.


---

## 22. Trade-offs and open questions

Every decision in this architecture carries a cost, and we make them explicit rather than pretend they are free.

The WYSIWYS-plus-simulation-plus-token verification path adds latency to every signature: intent decoding, full-state simulation, digest binding, and in-enclave verification all cost time. This is unambiguously worth it for institutional value transfers, but for high-frequency, low-value hot-wallet flows it is heavy. The resolution is a *pre-authorized envelope* mode in which policy approves a bounded class of transactions in advance — still digest-bound, still within the model — rather than weakening the invariants for speed. The exact envelope semantics should be revisited once real throughput figures are in hand.

The intent decoder and the simulator are a long, high-maintenance tail. Per-chain, per-contract decoding and simulation for true WYSIWYS is genuinely hard in the presence of proxy contracts, novel call-data, and chains with exotic execution models. We ship with EVM, Bitcoin, and Solana first-class and a "decode-and-simulate unavailable" degraded mode that policy treats as high-risk by default — never silently approving what it cannot interpret. This is the component with the highest ongoing engineering burden, and it should be budgeted as such permanently rather than as a one-time build.

The CGGMP21-versus-DKLS23 default is a real tension between safety and throughput, and the right answer is not a global choice. Protocol is a key-group property, selected by asset value and risk appetite, and the default split should be revisited after observing the real signing mix in production.

Operator-sovereign versus client-sovereign cold recovery trades security against client operational burden. Client-sovereign is the correct institutional default and the strongest expression of I-7, but it requires the client to run a key ceremony, which is operationally heavier. We offer both and default regulated tenants to client-sovereign.

Post-quantum migration remains genuinely open: no vetted threshold-PQ signature scheme is production-ready, and the responsible posture is to keep the agility seam clean and the transport and backups hybrid-protected now, then migrate signing when a vetted library and NIST threshold guidance exist. This is the open question most likely to force real work in the coming years, and the architecture is shaped to absorb it as a re-share rather than a rebuild.

---

## 23. Build sequence and roadmap

The sequencing principle is to build the moat before the breadth, because the moat is what is structurally hard to copy and the breadth is a fundable grind.

1. **CAL skeleton and invariants.** Implement the domain core, the SPI ports, and invariants I-1 through I-8 with a mock `SigningPort`. Lock the signing-path contract (§6) first — everything hangs off it, and getting the contract right before any backend exists is what keeps the abstraction clean.
2. **CGGMP21 MPC backend** behind `SigningPort`: DKG, sign, and proactive-secret-sharing refresh.
3. **Policy engine, token issuance, and in-enclave `Admit()`.** This is the moat (I-2, I-3, I-4); build it before chain breadth.
4. **Intent decoder, transaction simulator, and WYSIWYS render** for EVM, with passkey approval binding over `payloadDigest ‖ simDigest`.
5. **Transparency log and external witnessing** (I-8).
6. **HSM backend (PKCS#11)** behind the same `SigningPort` — the proof that the abstraction is real, not aspirational.
7. **Chain breadth** — FROST for Ed25519 and Solana, Schnorr for Taproot — together with SDKs, webhooks, and delegated signing.
8. **Recovery rails** (I-7) and **compliance evidence automation**.
9. **Forward capabilities, on the seams already cut:** AI advisory enrichment (I-9), conditional authorization and settlement (I-10), permissioned-token and account-abstraction support (I-11), selective disclosure (I-12), zero-knowledge compliance proofs, and cross-institutional key-groups.

Steps 1 through 4 yield something the incumbent structurally does not have. Steps 5 through 8 are the long grind to parity on breadth. Step 9 is the forward roadmap, and because every item in it lands on a seam cut in steps 1 through 5, none of it requires re-architecture — which is the entire point of the future-proofing discipline this document is built around.

---

## 24. Appendix A — invariant reference

| ID | Invariant | Category |
|---|---|---|
| I-1 | No complete private key in cleartext at any node, ever | Key secrecy |
| I-2 | WYSIWYS payload binding: signed ≡ approved ≡ token bytes | Intent integrity (spine) |
| I-3 | No signature without a valid, fresh, single-use decision token | Policy enforcement |
| I-4 | Every policy decision is deterministic and replayable | Auditability |
| I-5 | Every signing party runs in an attested, verified enclave | Trust anchoring |
| I-6 | Lifecycle operations never change the public key / address | Operational continuity |
| I-7 | The operator alone cannot reconstruct a client's keys | Client sovereignty |
| I-8 | History is append-only and externally verifiable | Tamper-evidence |
| I-9 | Intelligence is a signed input to policy, never the decision | AI governance |
| I-10 | Conditional authorizations release only on proven conditions | Settlement integrity |
| I-11 | Asset-level transfer restrictions honoured before authorization | Permissioned assets |
| I-12 | Every sensitive record supports authorised selective disclosure | Privacy / audit balance |

## 25. Appendix B — glossary

**CAL** — Custody Abstraction Layer; the hexagonal domain core whose ports render every backend an adapter.
**CanonicalIntent** — the deterministic, normalised representation of a proposed transaction over which policy is evaluated.
**CGGMP21 / DKLS23 / FROST** — threshold signature protocols for ECDSA (first two) and EdDSA/Schnorr (last).
**DKG** — distributed key generation; produces shares without any party ever holding the whole key.
**payloadDigest** — the hash binding the human-approved bytes, the policy-admitted bytes, and the signed bytes.
**PolicyDecisionToken** — the signed artifact proving policy admitted a specific payload; verified per-party at `Admit()`.
**Proactive secret sharing (PSS)** — scheduled verifiable share refresh that changes shares without changing the public key.
**simDigest** — the hash of the simulated state diff, bound into the approver's signature so consent covers the outcome.
**TSSHOCK** — the GG18/GG20 threshold-ECDSA extraction vulnerability class that motivates CGGMP21 as the default.
**WYSIWYS** — What-You-See-Is-What-You-Sign; the property that approved bytes equal signed bytes (invariant I-2).

---

*End of document. CUSTODY-ARCH-001.*
