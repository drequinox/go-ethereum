---
name: dasg-protocol-security-review
description: Step-by-step security-property-driven review of a protocol or flow (custody wallet, key exchange, bridge, consensus), including PQC readiness. Use when given protocol or flow documentation to review; outputs findings and a review tracker.
---

# DASG Protocol Security Review (Security-Property-Driven Assurance)

Use when the user supplies protocol or flow documentation (sequence diagrams, specifications, architecture documents, code) and wants a security review.

## Core rule
Every conclusion follows one explicit chain: security claim -> adversary and assumptions -> protocol and attack analysis -> evidence -> qualified conclusion.
- Never record "no attack found" as Supported.
- A proof gives only conditional assurance until its assumptions are checked against the implementation.
- An LLM is never the verifier. LLM reasoning produces hypotheses, arguments and drafts (models, findings).
- Every conclusion carries an evidence type:
  - Proved: formal tool output (Tamarin, ProVerif, TLA+ model checker) with a passing executability lemma and mutation check, or a cited published proof whose assumptions have been checked against this system.
  - Argued: a written reasoning argument (human or LLM) that a named human has reviewed and signed off. Never presented as proof.
  - Tested: a reproduced test, fault-injection or negative-test result.
  - Asserted: a design claim not yet examined.
- Critical safety properties (authorisation binding, replay resistance, key secrecy, anything rated Critical or High) remain Unverified until Proved or Tested. Argued evidence is acceptable for them only as an interim position, stated as such.
- Present the method as a synthesis of established practice (NIST SP 800-160, IETF RFC 3552, NIST SP 800-57, symbolic and computational verification). Never call it "the best" method or watertight.

## Execution protocol (mandatory)
- Run the steps strictly in order. After each step, output its deliverable under a heading "Step N" before starting the next.
- Every protocol fact cites its source (document + section, or file + line). Anything inferred is labelled "Inferred". Never invent message fields, verifiers or behaviour; record unknowns as open questions.
- Gate after Step 3: if a critical flow cannot be reconstructed, mark that flow Blocked, list the missing information as questions to the architects, and continue only with the flows that are complete.
- Facts about standards, attacks or incidents taken from memory are marked "verify before citing". When web search is available, check current standards status before stating it.
- Formal claims: "Proved" only when tool output is shown; otherwise "Model written, not run".
- After Phase D and before the final report, run an independent second pass. If the `dasg-protocol-refuter` agent is available (VS Code Copilot agent mode, Claude Code, Cowork), delegate to it, passing only the documentation, adversary model and claimed properties with their levels and evidence types, never your analysis. If subagents are unavailable (claude.ai chat), re-read as a hostile reviewer trying to refute each Supported status, and say that the second pass was not independent.

## Property classes (use these terms precisely)
- Invariant: a condition true in every reachable state (checked on one state). Example: ledger balance equals on-chain balance minus pending withdrawals.
- Safety: "something bad never happens", over the history of events; every invariant is a safety property, not every safety property is an invariant. A violation is a finite trace. Example: a signature occurs only after a matching approval of the exact digest, and each approval yields at most one signature (injective agreement). Secrecy ("the attacker never learns the key") is safety.
- Liveness: "something good eventually happens". A violation is an infinite run; proofs always depend on stated fairness and network assumptions.
- Hyperproperty: compares runs (unlinkability, strong secrecy, noninterference). Include only if privacy is claimed; otherwise state out of scope.

Liveness rule: prove safety for every critical property. Prove liveness under stated assumptions wherever it is claimed as a security guarantee, which is mandatory whenever a deadline turns delay into loss (timelocks, challenge or fraud-proof windows, HTLC or channel expiries, timelocked recovery) and for consensus. Otherwise treat liveness as availability: assess by failure testing (L3) or mark out of scope with a justification. Never imply liveness was proved when it was not.

## Roles (humans decide; the LLM drafts)
| Item | Proposes | Confirms or decides |
| --- | --- | --- |
| Security objectives | Security architect | Business and risk owner |
| Protocol specification (actual behaviour) | Reviewer reconstructs | System architects confirm it is correct |
| Security properties | Security architect formalises | Architects confirm intended behaviour; cryptographers review cryptographic properties |
| Adversary model and scope | Security architect | Risk owner agrees |
| Findings and status | Reviewer | Named peer reviewer signs off |
| Residual risk | Reviewer | Named risk owner accepts |
Never present an LLM-drafted property, specification or adversary model as agreed until the named human has confirmed it.

## Step 0 - Inputs
1. Domain profile (see Profiles). Ask once if unclear; default to Generic.
2. Evidence available: design documents only (L1), code and configuration (L2), test environment (L3).
3. Scope: flows in and out; document versions or commit hash (findings are valid only for these).
4. Input completeness check against this list, in priority order; report what is missing:
   1. sequence diagrams with message fields (who sends what, who verifies what);
   2. component and trust-boundary diagram (services, network zones, HSMs or enclaves, third parties);
   3. API and message schemas (OpenAPI, protobuf, signing-request formats);
   4. policy and approval rules (quorum, whitelist, limits, how policy changes are authorised);
   5. key management design (DKG, share storage, backup, rotation, recovery, break-glass);
   6. cryptographic scheme name and version with its paper or proof;
   7. timeouts and deadlines (timelocks, recovery delays, expiries);
   8. data and key lifetimes (for PQC);
   9. existing threat model.
   HTML or wiki exports are acceptable. Diagrams embedded as images may lose content in text extraction: ask for diagram sources (PlantUML, Mermaid, draw.io XML) or the images themselves.

## Phase A - Scope
1. Security objectives (outcomes, not technologies).
2. Inventory every security-critical flow, entry points, dependencies, transitions to other flows, and third parties (RPC nodes, oracles, KMS, HSM vendors, cloud, CI/CD).
3. Reconstruct each protocol: messages, fields, encodings, verifiers, state transitions, trust boundaries, timeouts and deadlines. Separate documented behaviour from actual behaviour.

## Phase B - Model
4. Security properties, each classified as invariant, safety, liveness or hyperproperty. Bind to exact bytes (digest, transcript). Use injective agreement where replay matters. Consider: confidentiality, integrity, authentication, authorisation, freshness, auditability, availability, privacy.
5. Adversary model: in-scope and out-of-scope capabilities with justification; network control; corruption (static or adaptive; semi-honest or malicious; threshold); insiders and collusion; state rollback; concurrent sessions; physical or side-channel access; future quantum adversary (store-now-decrypt-later and later forgery).
6. Assumption register: each assumption, evidenced or merely asserted, owner. Always consider: randomness quality, clock and ordering assumptions, honest-majority or threshold, trusted hardware, third-party correctness, and the fairness/network assumptions behind any liveness claim.

### Phase B gate (mandatory sign-off before analysis)
Stop after Step 6. Present the reconstructed specification (Step 3), the property catalogue (Step 4), the adversary model (Step 5) and the assumption register (Step 6) for confirmation by the roles above. Record who confirmed each and the date in the tracker's Review Record sheet. Do not start Phase C until the user confirms the gate has passed, or explicitly instructs you to continue provisionally; in that case label every later conclusion "Provisional: Phase B not signed off". This prevents moving goalposts: properties and adversary capabilities are agreed before anyone knows whether they hold.

## Phase C - Analyse
7. Primitives and constructions: suitability, parameters, proof assumptions, known attacks, implementation hazards. Turn vague observations into specific, supportable claims. Include:
   - Randomness and key derivation: RNG source (NIST SP 800-90A/B/C), nonce generation, key separation; for BIP32, non-hardened derivation where a child private key plus the parent extended public key reveals the parent private key.
   - Side channels and faults: timing, power/EM, fault injection on signing.
   - Post-quantum readiness (7a).

### 7a. PQC assessment
- Cryptographic inventory: every algorithm, key size, location, owner, data or key lifetime.
- Quantum exposure: Shor breaks RSA, DH, ECDH, ECDSA, EdDSA and Schnorr (including secp256k1, P-256, Ed25519). Grover weakens symmetric ciphers and hashes; prefer AES-256 and SHA-384/512 or SHA-3 for long-term use.
- Harvest-now-decrypt-later: compare each confidential channel's or ciphertext's required confidentiality lifetime with migration time and the quantum timeline (Mosca: act now if lifetime + migration time > time to threat).
- Forgery risk: long-lived signing keys and public keys already exposed.
- Standards: FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA (final); FIPS 206 FN-DSA (check status); NIST SP 800-208 LMS/XMSS for firmware and code signing; NIST IR 8547 transition (check status; draft dates deprecate 112-bit RSA/ECC after 2030, disallow after 2035); UK NCSC timeline (discovery by 2028, priority migration by 2031, complete by 2035).
- Hybrid classical + PQ key establishment during transition; check the combiner.
- Crypto-agility and downgrade resistance of algorithm negotiation.
- HSM, enclave and library support; side-channel-hardened PQ implementations.
- Size impact on protocols, storage and fees.

8. Attack analysis: for each property, try to construct a violating execution: replay, reordering, substitution, reflection, impersonation, equivocation, collusion, concurrency, aborts, rollback, downgrade, timeout or race, resource exhaustion, malicious third party. Then check cross-flow composition (one flow undermining another, e.g. recovery or policy change bypassing signing controls). Cover every category in the active profile or mark it out of scope with justification.

## Phase D - Assure
9. Formal verification where consequence justifies it. Tool by property class:
   - Safety and secrecy against an active adversary (authentication, authorisation binding, replay): Tamarin or ProVerif. Delegate to the `dasg-tamarin-modeller` agent when available. See references/withdrawal_auth.spthy for a worked template.
   - Invariants and workflow state, concurrency, liveness with fairness: TLA+ (TLC or Apalache).
   - Computational security: published game-based or UC proofs, CryptoVerif or EasyCrypt; check the implementation meets every proof assumption.
   - Smart contracts: formal specification and symbolic execution.
   Every model needs: an executability lemma (the honest run completes), stated abstractions, and a mutation check (remove the security check and confirm the property becomes falsified; a property that still "holds" means the model is vacuous). A verified model proves the property only within that model.
   If no verification tool is available: write the model anyway and mark it "Model written, not run" with the exact command; write a step-by-step argument for the property, covering each attack in Step 8, and record the evidence type as Argued pending named human review. Critical properties stay Unverified. Point out that Tamarin is free and installs quickly (Homebrew, or WSL on Windows), so tool access should rarely be the reason a critical property is left unproved.
10. Implementation conformance (L2): code, configuration, libraries and versions, encoding, input validation, access enforcement, secrets handling, build and deployment integrity. Confirm the implementation performs every check the model relies on.
11. Adversarial and failure testing (L3): negative tests, fault injection, malformed messages, crash recovery, concurrency, malicious participants, state-machine fuzzing, backup restore; liveness scenarios (signer offline, network partition, retries).

## Phase E - Conclude
12. Classify each property with status, level AND evidence type, e.g. "Supported (L1, Proved), Unverified (L2)".
- Statuses: Supported | Violated | Unverified | Out of scope | Risk accepted.
- Levels: L1 Design | L2 Implementation | L3 Adversarial. Formal proofs are recorded as evidence at the level of the artefact modelled (a model of the design is L1).
- Evidence types: Proved | Argued | Tested | Asserted.
- Traceability: every objective -> property -> threat category -> tracker row; every row has a status. Report coverage gaps explicitly.
- Residual risks with a named owner for acceptance.
- Re-review triggers: protocol or library change, new participant or third party, algorithm change, newly disclosed attack class, change in quantum threat estimates or standards.

## Finding format
ID, title, flow, property (with class), threat category, adversary capability, hypothesis, evidence required, evidence type, status + level, named reviewer, severity (impact x exploitability under the stated adversary; Critical/High/Medium/Low/Info), acceptance condition. A disagreement must name the element it disputes: property, adversary, assumed behaviour, evidence or conclusion.

## Output
1. Review document: scope and evidence level, property catalogue with classes, adversary model, assumption register, PQC assessment, formal results (with tool output or "not run"), findings, residual risks, coverage gaps, open questions to architects.
2. Tracker spreadsheet based on assets/review-tracker-template.xlsx, one row per flow x property x adversary: ID, Flow, Property, Threat category, Adversary, Assumption, Attack scenario, Evidence, Evidence type, Level, Status, Severity, Owner, Ticket. Complete its Review Record sheet (documents and versions, Phase B gate sign-offs, peer reviewer, risk acceptance, tool versions). Its summary flags Critical or High properties marked Supported without Proved or Tested evidence; resolve every flagged row before issue. The template's pre-filled rows and Threat Catalogue sheet are for the custody wallet profile; for any other profile, replace them with the active profile's flows and categories.
Keep findings technical; remediation is tracked in tickets.

## Profiles

### Custody wallet (complete)
Central safety property: injective authorisation-to-signature correspondence on the exact signed digest (sighash or EIP-712 hash), under the current policy version, with no revocation between approval and signing.
Liveness: flows normally have no deadline (delay is availability); check every flow for timelocks, recovery delays or expiries, which make liveness a security property.
Mandatory categories:
- Approver display integrity (WYSIWYS): calldata decoding, delegatecall, proxy upgrades, EIP-712 rendering.
- Authorisation binding: digest, policy version, freshness, replay.
- Chain semantics: chain-ID and cross-chain replay, nonces, fee and RBF manipulation, UTXO change validation, token approvals and permits.
- Address integrity: deposit-address generation and display, whitelist changes, address poisoning.
- Key lifecycle: DKG and ceremony, share refresh, backup and restore, snapshot rollback of MPC state, destruction, derivation paths.
- Threshold implementation: nonce and presignature reuse or bias, required ZK and range proofs present, abort handling.
- Execution environment: HSM or enclave attestation, side channels, supply chain.
- Privileged paths: policy change, admin collusion, break-glass, recovery quorum at least as strong as signing quorum.
- Ledger reconciliation: internal ledger vs on-chain, reorgs, stuck transactions, trust in RPC or indexer data.
- Quantum: chain signature scheme is set by the chain, not the custodian; on-chain public key exposure (address reuse, key-path spends, P2PK); key-share transport and backups under classical KEMs are harvest-now-decrypt-later targets that lead to key compromise; maturity of threshold PQ signatures; dependency on chain governance for migration.
Additional standard: CCSS (cryptoconsortium.org).

### Key exchange / secure channel (stub; extend)
Safety: mutual authentication, key secrecy, forward secrecy, post-compromise security, downgrade resistance, transcript binding, key separation, hybrid PQ KEM correctness. Weight computational proofs and implementation state-machine fuzzing heavily.

### Bridge / cross-chain messaging (stub; extend)
Safety: message authenticity and uniqueness, replay across domains, validator or relayer set integrity and rotation, upgrade and admin keys. Liveness is a security property where challenge windows exist. Finality assumptions per chain.

### Consensus (stub; extend)
Safety (no conflicting finalised blocks) and liveness under the stated network model (synchronous, partially synchronous, asynchronous), both required. Fault threshold, equivocation accountability, reconfiguration. Use TLA+ or similar for liveness.

### Generic
Core procedure; derive categories from Step 8's attack list and RFC 3552.

## Style
Direct, technically precise, no overclaiming; concise, panel-ready wording.
