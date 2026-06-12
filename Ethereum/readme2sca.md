# Strategic & Future-Proofing Capabilities
## A Companion to CUSTODY-ARCH-001

**Document reference:** CUSTODY-STRAT-002
**Status:** Strategic capability register
**Audience:** Architecture review, product strategy, leadership, R&D planning
**Relationship to CUSTODY-ARCH-001:** This document does not restate the core architecture. It specifies the forward-looking, strategically differentiating capabilities that the platform must accommodate, grounds each in the current vendor landscape and the live research frontier, names the institutional need it serves, and states precisely what gap it fills and which architectural seam absorbs it.

---

## Table of contents

1. Purpose and method
2. The 2026 baseline — what the market already ships
3. The research frontier — what is becoming possible
4. How to read each capability entry
5. Capability register
   - 5.1 Post-quantum threshold signing and crypto-agility
   - 5.2 Full-state simulation and intent verification
   - 5.3 AI-assisted policy and anomaly intelligence
   - 5.4 Autonomous-agent and machine-to-machine custody
   - 5.5 Intent-based execution and MEV-protected settlement
   - 5.6 Conditional authorization and atomic settlement (DvP)
   - 5.7 Tokenized real-world assets and asset servicing
   - 5.8 Account abstraction and programmable accounts
   - 5.9 Staking, validator operations, and slashing protection
   - 5.10 Zero-knowledge proofs of reserves, solvency, and compliance
   - 5.11 Privacy with selective disclosure
   - 5.12 Programmable, jurisdiction-aware compliance and travel rule
   - 5.13 Cross-institution and decentralized custody networks
   - 5.14 Bridge and cross-chain risk containment
   - 5.15 Provable resilience and continuous recovery
   - 5.16 Confidential computing beyond the TEE trust assumption
6. Capability prioritisation matrix
7. Strategic synthesis — the three bets that matter
8. Sources and further reading

---

## 1. Purpose and method

The core architecture document specifies a custody platform built around a deterministic, verifiable signing spine. This companion answers a different question: *given where the market and the research are heading, which strategic capabilities must the platform be able to absorb, and what does it take to absorb them without compromising the spine?*

The method is deliberately empirical rather than speculative. Each capability below is grounded in three evidence bases gathered from the current landscape: what custody vendors are actually shipping or piloting as of mid-2026; what the cryptographic and systems research community is actively publishing and standardising; and what institutional buyers, regulators, and standards bodies are demanding. A capability earns a place in this register only when at least two of those three pressures are real and convergent. The aim is an authentic strategic register, not a feature wishlist — every entry names a concrete need, a concrete gap, and a concrete fill.

The governing discipline is the same one that shapes the core architecture: future-proofing is the practice of cutting the right *seams* now so that a capability we cannot fully build today arrives later as a new adapter behind a stable interface, never as a re-architecture. For each capability we therefore name the seam — typically a specific Custody Abstraction Layer port or domain invariant — that absorbs it.

---

## 2. The 2026 baseline — what the market already ships

To claim a platform is "better" and "future-proof," one must first be honest about where the incumbents already are, because the bar is high and rising. The current landscape establishes the floor.

The dominant institutional platforms — Fireblocks, BitGo, Anchorage, Copper, Dfns, Cobo, Fordefi, Ripple Custody, Hex Trust, Zodia, and others — have converged on MPC/TSS with key shares distributed across secure enclaves, a policy engine increasingly computed inside a trusted execution environment, and broad multi-chain coverage. Fireblocks alone reports securing trillions in cumulative transaction volume across hundreds of millions of wallets and thousands of institutional clients, with its policy engine running in a TEE and MPC-CMP as its threshold protocol. BitGo completed the first custody-sector IPO in early 2026 and holds an OCC national trust bank charter, and its acquisition of an SEC-registered transfer agent gives it a genuine foothold in tokenized real-world assets. The regulatory wrapper has become a primary axis of competition: NYDFS trust charters, OCC national trust charters, MiCA CASP authorisation ahead of the July 2026 deadline, and qualified-custodian status now decide procurement as much as the cryptography does.

Several forward capabilities are already moving from roadmap to product at these vendors. Quantum-resistant key-migration roadmaps aligned to the NIST post-quantum standards are in active development for late-2026 deployment at multiple custodians. AI-powered anomaly detection for transaction flows is being built into the larger platforms. Native staking with slashing protection, validator governance, and customisable delegation policies has moved, in the words of one custodian's 2026 prediction, "from optional to operational." Lightning Network channel management and Layer-2 treasury operations are now governed under unified policy engines. Embedded-wallet and Wallet-as-a-Service models, smart-account features such as session keys and gas sponsorship, and open-source signer architectures that explicitly market freedom from vendor lock-in are all live in the market. And purpose-built MPC custody for AI agents — with mandate-based spending limits, real-time risk checks, and built-in travel-rule compliance — has already shipped from at least one major vendor supporting eighty-plus chains.

The strategic implication is sharp. Most of the "futuristic" features a naive analysis would propose are, in 2026, either shipping or imminently shipping somewhere. Differentiation cannot come from the feature list alone. It must come from doing these things *on top of an architecture that closes the structural gaps the incumbents leave open* — the intent gap and the trusted-orchestrator gap from the core document — so that every advanced capability inherits WYSIWYS binding, token-gated signing, determinism, and verifiability for free. That is the thesis this register serves.

---

## 3. The research frontier — what is becoming possible

Three research currents materially change what a custody platform can promise over the next three to five years, and each has moved meaningfully in just the last twelve months.

The first is **threshold post-quantum signatures.** As recently as a year ago, the honest position was that no production-ready threshold-lattice signature scheme existed, which made post-quantum threshold custody a "keep the seam clean and wait" proposition. That position is now obsolete. NIST published its formal Multi-Party Threshold Cryptography call (IR 8214C) in January 2026, and a cluster of practical threshold ML-DSA constructions has emerged in the research literature — schemes such as Mithril and Trilithium, and constructions supporting up to sixty-four participants with identifiable aborts using novel short secret-sharing techniques, with per-party communication in the kilobyte-to-megabyte range and signing latencies measured in milliseconds in local settings. The implication is that threshold post-quantum signing is transitioning from "theoretically interesting" to "engineerable for small party counts," which is precisely the regime institutional custody operates in.

The second is **the maturation of classical threshold cryptography toward active-adaptive security with identifiable aborts.** The lineage from GG18/GG20 through CGGMP21 to DKLS-class protocols and fully-adaptive Schnorr threshold signatures has consolidated around the properties institutional custody actually needs: universal composability, proactive refresh, identifiable abort, and security against active and adaptive adversaries. NIST's threshold EdDSA/Schnorr notes are being extended specifically to integrate active-adaptive security perspectives. This is not exotic research anymore; it is the standardisation of the exact properties the core architecture already mandates.

The third is **the convergence of intent-based execution, zero-knowledge proof systems, and confidential computing** into the application and settlement layer. Intent-based architectures — where a user signs a declarative intent and competing solvers execute it — have become the mainstream MEV-protection mechanism, structurally preventing front-running by keeping order details out of the public mempool. Zero-knowledge proofs are moving proof-of-reserves from a marketing exercise toward genuine cryptographic attestation, and are being explored for proving regulatory compliance and even for compressing the on-chain verification cost of post-quantum signatures. And the emergence of autonomous AI agents transacting in stablecoins has created an entirely new custody category — machine-to-machine settlement under programmatic mandates — that did not meaningfully exist two years ago.

A platform designed today must be built to absorb all three currents as they land. The register below specifies how.

---

## 4. How to read each capability entry

Every capability in the register follows the same five-part structure, so the strategic logic is auditable rather than asserted.

**What it is** — a precise statement of the capability. **Market signal** — what vendors are shipping, piloting, or roadmapping, grounded in the current landscape. **Research signal** — what the research and standards frontier is producing. **The need** — the concrete institutional, regulatory, or operational pressure that makes this strategic rather than ornamental. **The gap and the fill** — what is missing in the incumbent approach and exactly what the platform builds, including the architectural seam (CAL port or invariant) that absorbs it without disturbing the signing spine.

---

## 5. Capability register

### 5.1 Post-quantum threshold signing and crypto-agility

**What it is.** The ability to generate and use threshold signatures under post-quantum signature schemes, and to migrate existing key-groups from classical to post-quantum protocols without changing the platform's architecture — backed by a discipline of cryptographic agility in which every primitive is versioned and swappable.

**Market signal.** Quantum-resistant key-migration roadmaps aligned to the NIST post-quantum standards are in active development across multiple major custodians for late-2026 deployment, and at least one institutional guide now lists "quantum-resistant key migration roadmaps" as a distinct evaluation axis. The SEC has begun referencing NIST post-quantum algorithms in proposed digital-asset custody frameworks, and regulatory bodies in the US and EMEA are signalling that post-quantum readiness will become a component of SOC 2 and ISO 27001 audits for financial institutions. The "wait and see" posture is, in the words of one 2026 framework, "no longer defensible at the board level."

**Research signal.** This is the frontier that moved most in the last year. NIST's Multi-Party Threshold Cryptography call (IR 8214C) was published in January 2026, and practical threshold ML-DSA schemes have emerged — Mithril, Trilithium, and constructions supporting up to sixty-four parties with identifiable aborts — with per-party communication in the kilobyte-to-megabyte range and millisecond signing latencies for the small party counts that custody actually uses. The standardised NIST primitives (FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA) are now the targets. The known hard problem is that thresholdising lattice signatures is mathematically far more complex than thresholdising secp256k1 and requires a substantial overhaul of the TSS stack; signature and key sizes are also materially larger, with consequences for on-chain gas and storage.

**The need.** The harvest-now-decrypt-later threat is immediate for confidentiality even though the signature-forgery threat is years out: adversaries can record public keys and encrypted transport today and break them later. Roughly a third of all Bitcoin already sits in addresses with exposed public keys. Institutions with multi-decade custody horizons — pension assets, sovereign holdings, long-dated tokenized securities — cannot credibly claim a twenty-five-year custody guarantee on a cryptographic foundation that a cryptographically-relevant quantum computer breaks.

**The gap and the fill.** Incumbent roadmaps largely treat post-quantum as a future migration event. The platform treats it as a *structural property present now*: hybrid classical-plus-post-quantum key establishment protects transport and cold backups today (closing the harvest-now exposure immediately), while the signing scheme remains a versioned property of each key-group with a defined `migrationPath`. When a vetted threshold-ML-DSA library and NIST threshold guidance mature, adoption is a re-share under `KeyLifecyclePort` and a new adapter behind `SigningPort` — not a platform rebuild. The seam is the protocol-as-key-group-property design and the crypto-agility discipline; the invariant preserved is I-6 (lifecycle operations never change the public key). This is the single capability where the platform should aim to be visibly ahead of the market rather than at parity, because the seam already exists and the research has now caught up to it.

---

### 5.2 Full-state simulation and intent verification

**What it is.** Before any approval, the platform forks the relevant chain at current state, executes the proposed transaction, and presents the *actual resulting state diff* — balances moved, allowances granted, ownership and admin rights changed — and binds the hash of that simulated outcome into the approver's signature and the policy decision.

**Market signal.** Transaction-simulation and pre-trade risk tooling exists across the ecosystem, but it is typically a control-plane convenience that informs a human, not a cryptographically bound precondition of signing. The larger platforms are adding AI-powered anomaly detection on flows; simulation as a *bound* element of the authorization is not yet standard.

**Research signal.** The structural lesson of the 2025 catastrophic losses — most prominently the $1.5B Bybit/Lazarus incident — is that the failures were not breaks of the signing mathematics but breaks of the binding between what a human approved and what was signed. Research and incident analysis converge on the conclusion that decoded call-data is insufficient for human authorization because malicious effects can be obscured behind proxy contracts and delegatecall patterns; only the simulated *outcome* reliably reveals them.

**The need.** Institutional approvers cannot be expected to interpret raw or even decoded call-data for complex DeFi and smart-account interactions. They need to approve an outcome they can understand — "this moves 40M USDC to address X and grants no allowances" — and they need a cryptographic guarantee that the outcome they approved is the one that executes.

**The gap and the fill.** The incumbent request-signing model binds a human's passkey to an API request, not to a broadcast payload or its effects. The platform makes full-state simulation a first-class custody primitive: the approver signs over `payloadDigest ‖ simDigest`, and the in-enclave `AuthorisationVerifier.Admit()` refuses to sign unless the payload and its simulated outcome match what was approved. This is the strongest possible expression of invariant I-2 (WYSIWYS payload binding) and it catches the entire approve-unlimited / setOwner / delegatecall-manipulation class semantically. The seam is the Intent Decoder and Simulator in the signing path; the maintenance cost — per-chain, per-contract decoding for proxies and novel call-data — is the highest in the platform and must be budgeted permanently, with a degraded "decode-unavailable → high-risk" mode as the safe default.

---

### 5.3 AI-assisted policy and anomaly intelligence

**What it is.** Machine-learning models that score transaction risk, detect behavioural anomalies, assist intent decoding for novel contracts, and correlate against threat intelligence — with every model output consumed as a *signed input* to the deterministic policy engine, never as the decision itself.

**Market signal.** AI-powered anomaly detection for transaction flows is in active development at major custodians for late-2026 deployment, and is now cited as a force reshaping institutional custody requirements alongside post-quantum cryptography. The market direction is clear; the governance discipline around it is not yet standardised.

**Research signal.** The broader AI-and-crypto convergence is one of the dominant investment themes of 2026, with a large and rising share of crypto venture funding going to companies also building AI. The unresolved question across the field is governance: how to use model intelligence without sacrificing the determinism, replayability, and auditability that regulated custody requires.

**The need.** Institutions need intelligence that catches the anomalous transaction the static rule misses — the approver signing at an unusual hour to a freshly created address, the contract interaction that pattern-matches a known exploit — without introducing an opaque, non-replayable component into the authorization path that a regulator cannot examine.

**The gap and the fill.** The naive version of "AI-enhanced custody" makes a model the approver, which is non-replayable, uncertifiable, and indefensible to a regulator asking why a transfer was authorised. The platform enforces invariant I-9: intelligence is a signed input to a deterministic decision, never the decision. Model outputs — risk scores, anomaly flags, decoded-intent assistance, threat-intel matches — are snapshotted, hashed, bound into the canonical intent, and consumed by human-authored, versioned policy rules ("if risk-score > X and amount > Y and destination not allowlisted, escalate to 3-of-5 quorum or deny"). The decision stays a pure, replayable function of those inputs. The seam is the enrichment service and the `PolicyEnrichmentPort`; the invariants preserved are I-4 (determinism) and I-9 (intelligence governance). This is a capability where the platform should be visibly *more disciplined* than the market, turning a governance constraint into an audit advantage.

---

### 5.4 Autonomous-agent and machine-to-machine custody

**What it is.** Custody for wallets controlled by autonomous AI agents, with cryptographically enforced spending mandates, per-agent identity, real-time risk gating, and full auditability of agent-initiated transactions.

**Market signal.** This is among the fastest-moving categories in the market. At least one major vendor has shipped a purpose-built MPC custody solution for AI agents supporting eighty-plus chains, with mandate-based spending limits, real-time risk checks, and built-in travel-rule compliance. Emerging agent-payment standards define a flow of mandate creation, policy evaluation, KYC/AML screening, settlement, and receipt-and-proof generation, with append-only audit logs of all intents and settlements. Autonomous agents transacting in stablecoins — the default "agent money" because of programmability, always-on settlement, and price stability — are moving from prototype to pilot, and AI wallets capable of self-managing assets are now in pilot programmes.

**Research signal.** The identity and authorization model for agents is the active research question: proof-of-personhood via zero-knowledge cryptography, short-lived workload identities that authenticate agents without static credentials, and the unresolved legal status of software that holds and moves funds. Current law treats agents as tools and holds developers responsible, which places the entire burden of control on the custody and policy layer.

**The need.** When software autonomously moves institutional funds, the spending mandate is the only thing standing between a useful agent and an unbounded liability. Institutions need agent mandates that are cryptographically enforced rather than advisory, with per-agent identity, hard spending and counterparty limits, and an audit trail that survives examination.

**The gap and the fill.** The platform is unusually well-positioned here because agent custody is *exactly* the case the core architecture was built for. An agent mandate is a policy. An agent's intent is a canonical intent that gets simulated, bound, and token-gated like any other. The platform issues each agent a constrained credential, expresses its mandate as a versioned policy (spending limits, allowed counterparties, validity windows, conditional flows), and routes every agent-initiated transaction through the same WYSIWYS-bound, token-gated signing path — so an agent cannot exceed its mandate even if the agent itself is compromised or misaligned, because the signing parties refuse without a valid `PolicyDecisionToken` for the specific bounded action. Conditional authorization (5.6) lets an agent's payment be gated on proof of a counter-obligation. The seam is the existing policy engine, credential model, and signing path; no new trust assumption is introduced. This is a capability the platform can credibly claim to do *more safely* than agent-custody-first vendors, precisely because the safety is structural rather than bolted on.

---

### 5.5 Intent-based execution and MEV-protected settlement

**What it is.** Support for signing declarative intents (rather than raw transactions) that competing solvers execute, and for routing transactions through private channels that shield them from the public mempool, protecting institutional flow from front-running and sandwich attacks.

**Market signal.** Intent-based architectures are now the mainstream MEV-protection mechanism. Platforms such as CoW Swap and 1inch Fusion let a user sign a gasless EIP-712 typed-data intent to trade at a target price, with solvers competing to execute and bearing the MEV risk; CoW's solvers bond stake that is slashable for misbehaviour. Private-mempool and private-RPC routing — Flashbots Protect, MEV-Blocker, and chain-native private mempools — are widely used by institutional traders, and at least one major chain now offers private-mempool MEV protection as a one-line RPC integration. Execution quality in 2025 came to look "less like an adversarial byproduct and more like an institutional supply chain."

**Research signal.** The field has consolidated around a small set of mechanisms — intent-based architecture, private mempools, batch auctions, and shared sequencing — with explicit recognition that institutional large-position trades tolerate the seconds-to-minutes latency of batch auctions in exchange for execution integrity. MEV is understood as universal across chains, not Ethereum-specific.

**The need.** Large institutional transactions broadcast to a public mempool are visibly exploitable; the hidden tax of front-running and sandwiching is a direct cost to the institution and a fiduciary concern. Custody that signs a raw transaction into a public mempool is leaving execution quality on the table.

**The gap and the fill.** Most custody platforms sign a raw transaction and broadcast it; execution protection is the client's problem. The platform treats execution venue as a *policy-governed property of the signing request*. An intent is a canonical intent that gets simulated and bound exactly like a transaction — and because the signed object is a declarative intent rather than a raw transaction, WYSIWYS binding extends naturally to "what the human approved is the intent the solver must satisfy." Broadcast routing (public mempool, private RPC, intent pool) becomes a policy decision recorded in the audit log. The seam is the `TransportPort` for routing and the existing intent-binding machinery for the intent itself; invariant I-2 extends to intents without modification. Solver and venue risk are screened through the same threat-intelligence enrichment as any counterparty.

---

### 5.6 Conditional authorization and atomic settlement (DvP)

**What it is.** Signatures that are assembled only when an external condition is cryptographically proven true — enabling delivery-versus-payment, escrow, milestone release, time-locked and condition-locked transfers, hashed-timelock cross-chain swaps, and multi-leg atomic settlement.

**Market signal.** Atomic settlement and delivery-versus-payment are central to the institutional-DeFi pilots regulators are running — Singapore's Project Guardian explicitly tests tokenized collateral, automated settlement, and regulated liquidity pools. Off-exchange settlement networks that let institutions settle without rebroadcasting addresses are a primary competitive feature of the largest custody networks. Agent-payment standards build conditional flows and receipt-and-proof generation into the settlement path.

**Research signal.** Hashed-timelock contracts, atomic-swap constructions, and conditional-payment cryptography are mature; the frontier is composing them into institutional settlement with proper proof verification and into the agent economy as programmatic conditional flows.

**The need.** Institutional settlement is rarely a one-legged transfer. It is delivery against payment, release against milestone, swap against swap — and the institution needs a guarantee that its leg executes only if the counter-leg does, eliminating principal risk without a trusted intermediary.

**The gap and the fill.** Most custody platforms have no native concept of conditional release; settlement coordination is handled off-platform by a trusted party. The platform generalises the `PolicyDecisionToken` so it can encode named conditions, and the in-enclave `AuthorisationVerifier` refuses to admit a signature until the `conditionProofs` it carries satisfy those conditions. This single generalisation turns one mechanism into an entire settlement product line — DvP, escrow, milestone release, HTLC swaps, multi-leg baskets — with none of them a special case in the signing path. The seam is the `ConditionPort` and the condition fields already specified in the token; the invariant is I-10 (conditional authorizations release only on proven conditions).


---

### 5.7 Tokenized real-world assets and asset servicing

**What it is.** Native custody of tokenized real-world assets — tokenized treasuries, money-market funds, private credit, securities — under permissioned token standards that carry transfer restrictions and identity gating, together with the asset-servicing lifecycle those assets require: coupons, redemptions, corporate actions, voting, and rebasing.

**Market signal.** This is now a core battleground rather than a frontier. Tokenized fund assets under management crossed twenty billion dollars in early 2026, concentrated among a handful of institutional custodians. BitGo acquired an SEC-registered transfer agent to gain a foothold in RWA tokenization; Anchorage, Fireblocks, Coinbase Custody, and Komainu compete on which tokenized funds (BUIDL, OUSG, and others) they support and under which regulatory wrapper. Tokenization is expected to expand beyond treasuries into tokenized funds, private markets, and consumer applications, bringing distribution and compliance — not just issuance — on chain. Custody guides now list corporate-actions handling for tokenized securities and interoperability between blockchain and traditional finance as explicit requirements.

**Research signal.** Permissioned-token standards (the ERC-3643 / T-REX lineage and successors) embed transfer restrictions, on-chain identity gating, and issuer-controlled rules directly into the asset. The research-and-standards direction is toward on-chain identity attestations and compliance-by-construction, where eligibility is enforced at the token layer.

**The need.** A custody platform that assumes unrestricted bearer assets cannot hold the assets institutions are actually issuing. Tokenized securities can *reject a transfer at the asset layer*, require holder eligibility as a precondition, and demand servicing actions over their lifecycle. An institution custodying a tokenized fund needs the platform to understand redemption, coupon, and corporate-action flows, not merely to hold a key.

**The gap and the fill.** Many custody platforms model an account as a keypair holding a bearer balance. The platform makes permissioned-token semantics native in the `AccountPort`: it understands that a transfer can be rejected by the asset, that eligibility is a precondition, and it never produces a signature for a transfer the token will reject on-chain — enforced as invariant I-11 (asset-level transfer restrictions evaluated before authorization). The data model carries an asset-lifecycle seam so a held position can have servicing events acted on it under policy, positioning the platform as a custodian rather than a keystore. The seam is the `AccountPort` permissioned-token adapter and the `AssetPosition` lifecycle model; the invariant is I-11.

---

### 5.8 Account abstraction and programmable accounts

**What it is.** The ability to custody, co-sign for, and reason about smart-contract accounts — ERC-4337 and ERC-7579 modular accounts, session keys, gas sponsorship, and intent-based execution — rather than only externally-owned-account keypairs.

**Market signal.** Smart-account features are live across the market. Open-source signer platforms market session keys, gas sponsorship, and modular architecture explicitly as freedom from vendor lock-in; embedded-wallet providers build account abstraction into consumer and institutional products; the broader direction of travel is that modular smart accounts become a default account model rather than a niche.

**Research signal.** The account-abstraction standards (ERC-4337 bundlers and paymasters, ERC-7579 modular account interfaces) are maturing, and account abstraction is increasingly proposed as the *mechanism* for other migrations — including, in some chains' post-quantum plans, as the vehicle for migrating user wallets to post-quantum signatures via a protocol-level transition.

**The need.** As institutional activity moves onto smart accounts — for session-scoped delegation, sponsored gas, batched operations, and programmable spending rules — custody must be able to govern those accounts: approving module installs, issuing session keys under policy, and reasoning about paymaster relationships. A custody platform that can only sign EOA transactions is increasingly blind to how institutions actually operate on chain.

**The gap and the fill.** Platforms built solely around "account is a keypair" cannot govern programmable accounts. The platform's `AccountPort` models "an account is a programmable contract with its own rules" alongside the keypair model, so it can co-sign smart-account operations and bring module installs, session-key issuance, and paymaster relationships under the same policy and signing discipline as ordinary transfers. Session keys, in particular, are governed as time- and scope-bounded policies, with the same WYSIWYS and token-gating guarantees. The seam is the `AccountPort` smart-account adapter; the signing spine and invariants are unchanged.

---

### 5.9 Staking, validator operations, and slashing protection

**What it is.** Native support for proof-of-stake validator operations — staking and unstaking under policy, withdrawal-credential management, slashing-risk monitoring and protection, and governance participation — across the networks institutions hold.

**Market signal.** Institutional staking has moved, per one custodian's 2026 outlook, "from optional to operational." Custodians now compete on staking yields, slashing-insurance coverage, validator governance, and customisable delegation policies, with real-time monitoring of slashing risk built into policy engines. Unified governance frameworks now span on-chain holdings, Lightning liquidity, Layer-2 operations, and native staking under one custody umbrella. A March 2026 joint SEC/CFTC release classifying staking rewards as non-securities cleared a significant regulatory path, and staking ETFs have emerged. Slashing-protection coverage now spans provider treasuries, operator commitments, and third-party insurance.

**Research signal.** The institutional framing has shifted from yield to capital efficiency and governance participation, with validator management, slashing risk, and reporting obligations recognised as demanding professional infrastructure and fiduciary-grade controls.

**The need.** Roughly thirty percent of ether is now staked, and institutions holding proof-of-stake assets that do not stake are leaving both yield and governance influence unused — while those that do stake take on slashing risk, withdrawal-credential complexity, and reporting obligations that demand professional controls. Custody must govern validator operations under the same policy and audit discipline as transfers.

**The gap and the fill.** Staking is often a bolt-on integration with its own separate controls. The platform treats validator operations as first-class policy-governed actions: staking, unstaking, and withdrawal-credential changes are canonical intents that get simulated, bound, and token-gated, with slashing-risk signals fed through the enrichment layer into policy (so a delegation that would breach a slashing-risk threshold is denied or escalated). Withdrawal credentials are themselves key material under the platform's threshold and recovery guarantees. The seam is a validator-operations `AccountPort` adapter plus enrichment signals; the signing spine and invariants carry over directly.

---

### 5.10 Zero-knowledge proofs of reserves, solvency, and compliance

**What it is.** The ability to produce cryptographic proofs — proof of reserves, proof of solvency, and proof of policy compliance — that let an auditor, counterparty, or regulator verify a claim without the platform exposing every underlying position or the internals of its policies.

**Market signal.** Proof of reserves has shifted from "marketing tool" to a genuine expectation, with institutional custody guides now listing transparent proof-of-reserves and on-chain attestations alongside SOC reports and penetration tests as core due-diligence items. The GENIUS Act and parallel stablecoin frameworks in Singapore, Hong Kong, Canada, and South Korea mandate one-to-one reserve backing with regular attestation, making provable reserves a regulatory requirement rather than a courtesy. Privacy-preserving custody using zero-knowledge proofs to enable transaction privacy while maintaining auditability is explicitly named as an emerging custody model.

**Research signal.** Zero-knowledge proof systems are maturing rapidly and are being applied to reserves, to compliance attestation, and even to compressing the on-chain verification cost of post-quantum signatures. The direction is from "trust the operator's attestation" toward "verify the operator's proof."

**The need.** Institutions and regulators need to verify that a custodian holds what it claims and that signatures were issued under valid policy — without forcing the custodian to dox every client position or expose proprietary policy logic, and without relying on a trusted auditor's periodic word. The endgame is a regulator who *verifies* rather than *investigates*.

**The gap and the fill.** Incumbent proof-of-reserves is typically an attestation backed by a trusted auditor and a Merkle-tree snapshot; policy compliance is asserted, not proven. The platform builds on its externally-witnessed transparency log toward genuine zero-knowledge attestation: proof of reserves and solvency without position disclosure, and proof that a given signature was issued under a valid policy decision against a valid intent, verifiable without revealing policy internals. This collapses audit cost and converts examination into verification. The seam is the transparency log as substrate plus a proof-generation service; invariant I-8 (append-only, externally verifiable history) is the foundation, extended from "verifiable log" to "verifiable proof."

---

### 5.11 Privacy with selective disclosure

**What it is.** Confidentiality of positions and transactions from the public, combined with full, authorised transparency to auditors and regulators — implemented as structured selective disclosure rather than an all-or-nothing visibility switch.

**Market signal.** Privacy-preserving custody is named as an emerging model, combining zero-knowledge transaction privacy with maintained auditability and confidential computing that protects sensitive data during processing. Regulators are simultaneously demanding more transparency (travel rule, reserve disclosure) and institutions are demanding more confidentiality from competitors and the public — a tension the market has not cleanly resolved.

**Research signal.** Confidential computing, viewing-key constructions, and selective-disclosure credential systems are the active research areas, alongside privacy-focused chains that require specialised custody approaches.

**The need.** Institutions cannot operate with every position and counterparty visible to competitors on a public chain, yet they must give auditors and regulators complete visibility. These are reconcilable only if disclosure is a structured, authorised capability built in from the start.

**The gap and the fill.** Privacy retrofitted into a system designed in the clear is close to impossible. The platform enforces invariant I-12 from the schema upward: every sensitive record supports authorised selective disclosure via viewing-key or credential-gated access, scoped to specific parties for specific records with expiry. This is the same identity-and-eligibility rail that permissioned tokens (5.7) require, which is a reason to build it early even if initial deployments store records in the clear. The seam is the data model's `DisclosureGrant` construct and the encryption layer; the invariant is I-12.

---

### 5.12 Programmable, jurisdiction-aware compliance and travel rule

**What it is.** Compliance — sanctions screening, travel-rule originator/beneficiary exchange, KYC and eligibility gating, jurisdiction-specific transfer rules — expressed as a versioned, jurisdiction-scoped, hot-loadable policy layer that updates without a platform redeploy and records which ruleset version applied to each decision.

**Market signal.** Travel-rule compliance is built into the newest agent-payment and custody stacks as cross-border identity disclosure with append-only audit logs. Regulatory convergence is real — FATF, IOSCO, the FSB, and the OECD are pushing coordinated travel-rule and VASP expectations — even as enforcement remains uneven and compliance costs rise. The MiCA CASP July 2026 deadline, the GENIUS Act's multi-agency enforcement, and Singapore's and Hong Kong's frameworks all impose concrete, jurisdiction-specific obligations simultaneously.

**Research signal.** FATF's June 2025 update highlighted persistent gaps in travel-rule implementation specifically. The standards direction is toward on-chain identity attestations and "same risk, same rule" enforcement extending to DeFi, which pushes compliance logic toward something that must be expressed as code and updated continuously.

**The need.** A platform serving institutions across the US, EU, UK, Singapore, and Hong Kong must apply different, changing rules per jurisdiction, prove which rules applied to each historical decision, and update those rules faster than a release cycle when a sanctions list or a regulation changes.

**The gap and the fill.** Compliance is often hard-coded or release-bound, and "why was this approved under the rules in force that day" is hard to answer. The platform makes compliance a versioned, jurisdiction-scoped, hot-loadable policy layer, with travel-rule VASP identifiers modelled as first-class allowlist entities and every decision recording its compliance-ruleset version. Because policy evaluation is deterministic and logged (I-4), a regulator's question is answered by replaying the exact ruleset version against the logged intent. The transparency log doubles as the compliance-evidence engine. The seam is the compliance policy layer and the `PolicyEnrichmentPort` for screening snapshots; invariant I-4 makes it auditable.

---

### 5.13 Cross-institution and decentralized custody networks

**What it is.** Key-groups whose parties span multiple distinct institutions — client, custodian, independent recovery agent — such that no single organisation holds a signing or recovery quorum, enabling consortium and collaborative-custody models.

**Market signal.** Regulators increasingly want custody models where no single party can unilaterally access assets, and analysts note that distributed-trust MPC "matches what regulators want to see." Off-exchange settlement and collaborative-custody arrangements are growing, and the no-single-party-control property is becoming a procurement and regulatory expectation rather than a differentiator.

**Research signal.** The threshold-cryptography literature explicitly frames its purpose as distributing trust across operators so no operator is a critical point of failure, and NIST's threshold work targets exactly this multi-party trust distribution. Cross-organisational quorums are a natural extension of the same mathematics.

**The need.** The strongest form of "the operator cannot reconstruct the client's keys" is one where the operator is merely one party among several drawn from different organisations and jurisdictions. The most conservative institutional clients — and the regulators supervising them — want collusion across organisational boundaries to be required before assets can move unilaterally.

**The gap and the fill.** Most platforms distribute shares across one operator's own diversified infrastructure. The platform's party-membership model supports cross-organisational quorums from the outset, so a key-group can be composed of parties contributed by the client, the custodian, and an independent agent, with no single organisation holding a quorum — the strongest expression of invariant I-7 (the operator alone cannot reconstruct a client's keys). Building this into the membership model now avoids a structural rewrite later. The seam is the key-group party-membership model; the invariant is I-7.

---

### 5.14 Bridge and cross-chain risk containment

**What it is.** Treating cross-chain bridges — the dominant exploit vector in the ecosystem — as untrusted, policy-governed, threat-intelligence-screened boundaries rather than implicitly trusted infrastructure, while supporting chain-abstracted addressing and intent-based cross-chain settlement.

**Market signal.** Custodians now monitor cross-chain bridge exposure as a named risk, with policy engines automating approvals for Layer-2 bridge transactions and real-time monitoring of bridge exposure. Wrapped-asset and cross-chain operations are governed under unified policy frameworks, and bridge security for wrapped BTC is an explicit competitive axis.

**Research signal.** The bridge-hack taxonomy is a well-documented body of analysis; bridges concentrate value and trust assumptions in ways that have repeatedly proven catastrophic, and the research consensus is that bridge interactions warrant elevated, distinct controls.

**The need.** Institutions operating across chains and holding wrapped assets are exposed to the single most exploited component in the ecosystem. They need bridge interactions held to a higher control standard than ordinary transfers, with continuous exposure monitoring.

**The gap and the fill.** Where bridges are treated as ordinary destinations, their elevated risk is invisible to policy. The platform classifies bridge interactions as a distinct, high-risk action class: screened through threat-intelligence enrichment, subject to stricter policy (lower thresholds, mandatory quorum, exposure caps), and continuously monitored. Chain-abstracted settlement is supported, but the bridge boundary is always policy-governed rather than trusted. The seam is the threat-intelligence enrichment and a bridge-aware policy class; the invariants (I-2, I-3, I-9) carry over.

---

### 5.15 Provable resilience and continuous recovery

**What it is.** Recovery treated as a first-class, continuously-exercised capability that produces cryptographic proof-of-recoverability as a routine audit artifact, rather than an emergency procedure discovered to be broken at the worst moment.

**Market signal.** Operational resilience is now a regulatory mandate, with DORA in the EU requiring institutions to demonstrate — not merely assert — recovery capability. Custody due diligence increasingly examines tested recovery, segregation, and no-rehypothecation guarantees, and operational-resilience and cybersecurity standards are explicit licensing requirements in Singapore and elsewhere.

**Research signal.** Proactive secret sharing with verifiable refresh, threshold share repair, and the broader resilience literature provide the cryptographic basis for recovery that is both automated and provable.

**The need.** Regulators under DORA and parallel regimes require demonstrated recoverability; institutions require confidence that the three recovery rails actually work before a disaster, not after. Asserted recovery is no longer sufficient.

**The gap and the fill.** Recovery is often an untested emergency runbook. The platform makes recovery a continuously-exercised path: scheduled automated game-days exercise each of the three rails — operational, client-sovereign cold, and governance — and produce a cryptographic proof-of-recoverability as a standing audit artifact. The platform never waits for a disaster to learn whether recovery works. The seam is the recovery subsystem and its proof-generation; the invariants are I-6 (continuity) and I-7 (client sovereignty).

---

### 5.16 Confidential computing beyond the TEE trust assumption

**What it is.** Treating the trusted execution environment as one defensive layer rather than the trust root, combining attested enclaves with threshold distribution and, over time, zero-knowledge proofs of correct execution, so that no single mechanism's failure is catastrophic.

**Market signal.** The market leans heavily on TEEs — policy engines computed in a TEE, MPC shares refreshed inside secure enclaves, signing inside TEEs in tiered data centres are all standard. This concentration is itself a latent systemic risk the market under-discusses.

**Research signal.** TEEs, particularly earlier SGX generations, have a documented history of side-channel and microarchitectural vulnerabilities. The research direction is toward defence-in-depth — combining enclaves with threshold cryptography and verifiable computation rather than trusting the enclave alone — and toward confidential computing that protects data in use without making the hardware the sole trust anchor.

**The need.** A custody platform whose security rests on enclave integrity alone inherits every future TEE vulnerability as a single point of catastrophic failure. Institutions need a design where an enclave break is contained, not fatal.

**The gap and the fill.** Where the enclave is the trust root, its compromise is catastrophic. The platform deliberately spreads trust across three anchors — attested enclaves, threshold distribution, and the externally-witnessed transparency log — so that a side-channel break of the enclave is contained by the threshold, a threshold compromise is bounded and detected by the log, and a log compromise is caught by external witnesses. The `AttestationPort` verifies *evidence* rather than trusting a vendor, and the roadmap moves toward zero-knowledge proofs of correct execution as a fourth layer. The seam is the multi-anchor trust model and the `AttestationPort`; the invariant is I-5 (attested enclaves) held as one layer among several rather than the whole.


---

## 6. Capability prioritisation matrix

The register contains sixteen capabilities; not all are equally urgent or equally differentiating. The matrix below sorts them by two axes: how *strategically differentiating* the capability is (does it set the platform apart, or merely keep it at parity), and how much *architectural lead time* it needs (must the seam exist before launch, or can it be added later on an existing seam). The intersection identifies where to spend architectural attention first.

| Capability | Differentiation | Lead time | Recommended posture |
|---|---|---|---|
| 5.2 Full-state simulation + intent binding | Very high | Must precede launch | Build into the spine from day one — it *is* the moat |
| 5.1 Post-quantum threshold + crypto-agility | Very high | Seam now, adopt later | Be visibly ahead; seam exists, research has caught up |
| 5.3 AI-assisted policy (signed-input discipline) | High | Seam now | Differentiate on governance discipline, not model power |
| 5.6 Conditional authorization / DvP | High | Seam now | One mechanism unlocks a settlement product line |
| 5.13 Cross-institution key-groups | High | Must precede launch | Membership model is structural; retrofit is a rewrite |
| 5.10 ZK proofs of reserves / compliance | High | Build on log later | Transparency log is the substrate; add proofs over time |
| 5.11 Selective-disclosure privacy | Medium-high | Seam now (schema) | Privacy cannot be retrofitted; cut the schema seam early |
| 5.4 Autonomous-agent custody | High | On existing seams | Fast-moving market; platform is already well-positioned |
| 5.7 Tokenized RWA + asset servicing | High | Seam now | Core battleground; AccountPort must model restrictions |
| 5.16 Confidential computing beyond TEE | Medium-high | Architectural now | Multi-anchor trust model must be designed in, not added |
| 5.12 Programmable jurisdiction-aware compliance | Medium | Seam now | Parity-plus; differentiate via replayable evidence |
| 5.5 Intent-based / MEV-protected settlement | Medium | On existing seams | Extends intent binding and TransportPort |
| 5.8 Account abstraction | Medium | On existing seams | AccountPort extension; increasingly table stakes |
| 5.9 Staking / validator operations | Medium | On existing seams | Operational necessity; parity feature |
| 5.14 Bridge risk containment | Medium | On existing seams | Policy class + enrichment; mostly configuration |
| 5.15 Provable continuous recovery | Medium | Build on recovery | DORA-driven; differentiate via proof artifacts |

The reading of this matrix is that four capabilities demand architectural attention *before or at* launch because their seams are structural and cannot be retrofitted without a rewrite: full-state simulation (5.2), cross-institution key-groups (5.13), the multi-anchor trust model (5.16), and the privacy schema (5.11). Two more — post-quantum agility (5.1) and conditional authorization (5.6) — need their seams cut early even though adoption comes later, and they are where the platform can be visibly ahead of the market. Everything else lands on seams the core architecture already provides and can be sequenced by market demand.

---

## 7. Strategic synthesis — the three bets that matter

Sixteen capabilities is a register, not a strategy. Compressed to its essence, the platform's future-proofing rests on three bets, and getting these three right matters more than any individual feature.

**The first bet is that intent integrity becomes the defining custody guarantee.** The catastrophic losses of 2025 were not cryptographic breaks; they were breaks of the binding between human intention and machine action. Every serious institutional buyer now understands this in their bones. The platform that makes "the bytes you approved are the bytes that get signed, verified inside the trust boundary, against a simulated outcome you could actually understand" its central, provable promise wins the post-Bybit market. This is capability 5.2 fused with the core architecture's invariant I-2, and it is the bet the entire platform is organised around. Everything else is additive to it.

**The second bet is that cryptographic agility, with post-quantum readiness as its proof, becomes a compliance requirement rather than a research curiosity.** The evidence assembled here shows this transition already underway: NIST's threshold call published, practical threshold post-quantum schemes emerging, regulators referencing post-quantum algorithms in custody frameworks, and post-quantum readiness heading into SOC 2 and ISO 27001 audits. A platform whose every primitive is versioned and swappable, and which protects transport and backups against harvest-now-decrypt-later today, can credibly make the long-horizon custody guarantee that pension, sovereign, and long-dated tokenized-securities custody demands. This is capability 5.1, and it is the one place the platform should aim to be demonstrably ahead rather than at parity, because the seam already exists in the architecture and the research has now arrived to fill it.

**The third bet is that intelligence and compliance must be signed, deterministic inputs to a verifiable decision — never replacements for it.** This is the discipline that runs through capabilities 5.3, 5.4, 5.10, and 5.12. The market is racing to add AI to custody, autonomous agents to wallets, and ever more compliance logic to policy. The platform that adds all of these *as signed inputs to a deterministic, replayable, auditable signing path* — rather than as opaque components that a regulator cannot examine — turns the constraints of regulated custody into its competitive advantage. The audit becomes a verification, the agent mandate becomes cryptographically enforced, the compliance decision becomes replayable, and the AI risk score sharpens a human-authored rule rather than secretly making the decision. This bet is the reason the core architecture's insistence on determinism (invariant I-4) and signed-input intelligence (invariant I-9) is not a limitation but the platform's deepest source of durable differentiation.

The synthesis across all three: the incumbents are converging on the same feature list, and within a few years most of these capabilities will be available somewhere. The durable advantage is not having the features — it is having them on an architecture where each one inherits intent integrity, cryptographic agility, and verifiable determinism by construction. That is what "better than Dfns" and "future-proof" actually mean when made concrete, and it is what this register, together with CUSTODY-ARCH-001, specifies.

---

## 8. Sources and further reading

The capability entries above are grounded in the current vendor landscape, the cryptographic and standards research frontier, and the regulatory environment as of mid-2026. Principal source categories consulted:

- **Vendor and market analysis:** comparative custody analyses covering Fireblocks, BitGo, Anchorage, Copper, Dfns, Cobo, Fordefi, Ripple Custody, Hex Trust, and Zodia; tokenized-RWA and stablecoin custody comparisons; institutional Bitcoin and Ethereum custody guides addressing staking, Lightning, Layer-2, and quantum-migration roadmaps; and open-source / embedded-wallet platform documentation.
- **Cryptographic research and standards:** NIST Multi-Party Threshold Cryptography (IR 8214C, January 2026) and the associated threshold call; threshold ML-DSA constructions (Mithril, Trilithium, and related work supporting up to sixty-four parties with identifiable aborts); the CGGMP21 and DKLS protocol lineage and fully-adaptive Schnorr threshold work; and the FROST specification lineage.
- **Post-quantum policy and migration:** the US post-quantum regulatory framework (NSM-10 and the relevant Act), NIST FIPS 203/204/205, SEC signalling on post-quantum algorithms in custody frameworks, and CISO migration-framework analyses emphasising hybrid signatures and cryptographic agility.
- **Application and settlement frontier:** intent-based execution and MEV-protection analyses (CoW Protocol, 1inch Fusion, Flashbots Protect, private-mempool RPC), institutional-DeFi and atomic-settlement pilots (Project Guardian), and agent-payment standards and AI-agent custody platforms.
- **Compliance and resilience:** FATF, IOSCO, FSB, and OECD travel-rule and VASP guidance; MiCA, DORA, the GENIUS Act, and the Singapore, Hong Kong, Canada, and South Korea stablecoin frameworks; and proof-of-reserves and zero-knowledge attestation analyses.

Specific figures and claims cited inline (transaction volumes, AUM thresholds, staking percentages, regulatory dates, and research parameters) reflect the state of the landscape at the time of writing and should be re-verified at the point of any external use, as this is a fast-moving domain.

---

*End of document. CUSTODY-STRAT-002. Companion to CUSTODY-ARCH-001.*
