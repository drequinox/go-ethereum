# Capability Map & Maturity Model



---

## Purpose

This document defines the capability portfolio for an elite, institution-grade digital asset security function and the maturity model against which to benchmark and invest. It is framed for senior management: each capability is tied to a loss or regulatory rationale, with explicit build-versus-buy positioning to demonstrate disciplined investment rather than empire-building.

The guiding principle: lead with risk and obligation, not technology. The objective is not to rebuild commercial attribution platforms (Chainalysis, TRM, Elliptic), but to own the deep forensic, custody-specific, and institutional-memory layers that commercial tools cannot provide — and to integrate the whole into one defensible risk view.

---

## The Capability Portfolio

Twelve capabilities span four operating modes: proactive (1, 5, 7, 8, 10), reactive (2), protective (3, 4, 9, 11), and assurance/governance (6, 12). An elite group is credible across all four modes rather than strong in one.

| # | Capability | What it covers | Build / Buy | Why it resonates upward |
|---|-----------|----------------|-------------|-------------------------|
| 1 | **Threat Intelligence** | Actor tracking (DPRK/Lazarus clusters, exploit crews), attack-class research, ecosystem incident monitoring; feeds investigations | Build (TI graph) + buy (feeds) | Forward-looking risk reduction, not cleanup |
| 2 | **Forensic Investigation & IR** | On-chain tracing, attribution, exploit reconstruction, evidence-grade output, IR playbook (freeze/recovery, LE & exchange liaison) | Build (deep layer) + buy (attribution) | Demonstrable response capability when assets are touched |
| 3 | **Custody & Key-Management Security** | MPC/TSS security, HSM/enclave assurance, signing-fabric threat modeling, key-ceremony integrity | Build + assure | Protects the assets themselves — head is accountable |
| 4 | **Smart Contract & Protocol Security** | Pre-deployment review, integration risk (bridges/staking/DeFi), continuous contract monitoring | Build + buy (audits) | Prevents loss before it happens; gates integrations |
| 5 | **Cryptographic Assurance & Future-Proofing** | PQC migration, crypto-agility, curve/primitive review, hybrid signature roadmaps (NIST PQC) | Build | Signals multi-year thinking; board-level horizon |
| 6 | **Regulatory & Control Alignment** | Mapping capabilities to MiCA, DORA, Travel Rule, internal control framework; 2nd/3rd-line acceptance | Build + advise | Unlocks budget; ties spend to existing obligations |
| 7 | **Detection & Monitoring** | Real-time on-chain/off-chain monitoring of own addresses/contracts/counterparties; anomaly detection; alerting into IR | Build + buy | Operational backbone — continuous, not episodic |
| 8 | **Tokenized RWA & Stablecoin Security** | Issuer/redemption integrity, proof-of-reserves, run/liquidity stress, issuance & settlement contract logic | Build | Where institutional capital is moving (RWA/stablecoin growth) |
| 9 | **Staking & Validator Operations Security** | Slashing protection, validator/withdrawal key management, validator governance | Build + buy | Real loss surface generic custody security misses |
| 10 | **Counterparty & Protocol Risk Intelligence** | On-chain credit/concentration risk, exposure to custodians/exchanges/bridges/DeFi, contagion modeling | Buy + integrate | Single risk view; ties to treasury/credit decisions |
| 11 | **AI-Agent & Autonomous-System Security** | Agentic attack surface (prompt injection into signing flows, autonomous key access), signed-input discipline | Build | Newest frontier — very few teams have addressed it |
| 12 | **Offensive / Red-Team Capability** | Exploit reconstruction (e.g. threshold-signature PoCs), red-teaming signing fabric, adversarial policy/custody testing | Build | The credibility multiplier — break it to be trusted to defend it |

---

## Operating-Mode View

### Proactive — reduce risk before it materializes
- **Threat Intelligence (1):** actor and attack-class tracking feeding everything downstream.
- **Cryptographic Future-Proofing (5):** PQC migration and crypto-agility on a multi-year horizon.
- **Detection & Monitoring (7):** continuous visibility across own assets and counterparties.
- **RWA & Stablecoin Security (8):** securing the asset classes institutional capital is moving into.
- **Counterparty Risk Intelligence (10):** on-chain credit and contagion exposure.

### Reactive — respond when assets are touched
- **Forensic Investigation & IR (2):** trace, attribute, reconstruct, produce evidence-grade output.

### Protective — defend the assets directly
- **Custody & Key-Management Security (3):** the capability the head is personally accountable for.
- **Smart Contract & Protocol Security (4):** gate integrations and monitor deployed contracts.
- **Staking & Validator Security (9):** slashing protection and validator key management.
- **AI-Agent Security (11):** the emerging agentic attack surface into signing and treasury flows.

### Assurance / Governance — make capability acceptable and credible
- **Regulatory & Control Alignment (6):** converts technical depth into regulator- and audit-ready posture; typically what unlocks budget.
- **Offensive / Red-Team (12):** the credibility multiplier — a team that can break the stack is trusted to defend it.

---

## Maturity Model

Benchmark each pillar from Foundational to Elite. The Elite column is the target state; the gap between current and Elite drives the phased roadmap and budget ask.

| Pillar | Foundational | Established | Elite |
|--------|-------------|-------------|-------|
| **Threat Intelligence** | Ad-hoc incident reading | Structured TI feeds, manual analysis | Institutional TI graph accumulating memory; constrained-LLM extraction; proactive actor tracking |
| **Forensic & IR** | Rely on vendor reports | Defined IR playbook; basic tracing | Deep contract-level forensics + exploit reconstruction; evidence-grade; <24h MTTI |
| **Custody / Key Mgmt** | Vendor-trusted | Threat-modeled signing fabric | Continuous MPC/TSS assurance; differential testing; red-teamed ceremonies |
| **Contract / Protocol** | Pre-launch audit only | Integration risk reviews | Continuous monitoring + automated pre-deployment gate across all integrations |
| **Crypto Future-Proofing** | Aware of PQC | Migration plan drafted | Crypto-agile architecture; hybrid PQC piloted; emergency rotation tested |
| **Regulatory Alignment** | Reactive to exams | Mapped to MiCA/DORA | Control framework auto-evidenced; regulator-ready by default |
| **Detection / Monitoring** | Manual checks | Alerting on own assets | Real-time multi-source detection feeding automated IR |
| **RWA / Stablecoin** | Not covered | Proof-of-reserves manual | Automated PoR + run-risk modeling on issuance logic |
| **AI-Agent Security** | Not considered | Policy reviewed | Signed-input discipline enforced; agentic flows red-teamed |
| **Offensive / Red-Team** | None | Occasional exercises | Standing capability; attacks own stack continuously |

---

## Framing for Senior Management

### 1. Lead with risk and obligation
For each capability, state the loss scenarios it prevents, detects, or investigates, and the regulatory obligation it discharges. This beats a technology-first pitch and uses a decision-grade register.

### 2. Build-versus-buy clarity
**Buy:** commercial attribution (Chainalysis/TRM/Elliptic), third-party audits, HSM vendors, counterparty-risk feeds.
**Build:** deep contract forensics, the institutional TI graph, custody-specific tooling, exploit reconstruction.
Explicit positioning earns trust and avoids the rebuild objection.

### 3. A maturity-model roadmap
Present current-versus-target state per pillar with a phased plan. Senior management funds roadmaps, not vibes; a multi-phase structure over a defined horizon is fundable in a way a capability wish-list is not.

### 4. Metrics
- Mean time to detect / investigate (MTTD / MTTI).
- Coverage: % of assets and contracts under continuous monitoring.
- % of integrations security-reviewed pre-deployment.
- Incidents caught proactively versus reactively.
- Regulatory findings closed / control evidence automated.

---

## On the Forensic Analysis Tool

The contract-forensic tool is worth building — but positioned correctly. It is not a Chainalysis competitor; competing on labeled address clustering and exchange attribution is a losing proposition against vendors with years of data.

Its defensible value is threefold:

1. **Contract-level forensic depth** — bytecode, proxy resolution, storage-slot and full call-tree tracing — where commercial tools are weakest.
2. **Integration into the institutional TI graph** so investigations accumulate memory rather than living in a vendor silo.
3. **Custody-specific investigation** of the team's own contracts and incidents.

Pitched as the deep forensic and institutional-memory layer that complements commercial attribution and feeds the TI graph, it is complementary, defensible, and budget-safe.

---

