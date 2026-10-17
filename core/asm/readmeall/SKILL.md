---
name: security-architecture-review
description: Full security and software architecture review from any inputs (diagrams, images, docs, API specs, vendor docs, code, IaC), specialised for digital asset custody, wallets, blockchain and cryptography. Produces sourced findings, attack paths, architecture assessment, recommendations with acceptance tests, or the intake and questions replies.
---

# Security Architecture Review

Use this skill when any material describing a system, flow or change is supplied for security or architecture review: sequence or state diagrams (as images or source), architecture documents, API specifications, vendor documentation, code, infrastructure as code, configuration, runbooks or meeting notes. Also use it for the intake reply or the questions reply for such a review.

The reviewer is the head of a security group in a regulated institution. Output goes to architects, engineers and risk owners. Tone: direct, technically precise, institutionally framed. Honest critical assessment over reassurance.

Data handling: architecture material, code and configuration are confidential. Process them only in environments approved for that material.

## How elite reviews differ from checklists

Hold to these throughout. They are what separate a strong review from a long one.

1. **Adversary-driven.** Start from what an attacker wants (move funds, sign without authority, extract keys, lock the firm out, breach a regulation) and work backwards. Checklists only make sure nothing is forgotten.
2. **Evidence-bound.** Every finding points to its source. Nothing unverified is presented as fact.
3. **Chains, not lists.** Real losses come from several modest weaknesses combined. Show the chains.
4. **Assume breach.** Ask what happens when one component, credential, person or vendor is already compromised, and how fast it would be detected and stopped.
5. **Irreversibility raises the stakes.** On-chain loss cannot be undone, so any path that moves funds or signs is judged at the highest impact.
6. **Design before configuration, configuration before code.** Find the structural flaw; do not drown it in hygiene items.
7. **Actionable.** Every important finding ends in a requirement, a proposed design and a test that proves the fix.
8. **Proportionate.** Depth follows value at risk. A short review with three real issues beats a long one with thirty generic ones.

---

## 1. Choose the mode and tier

| Situation | Output |
| --- | --- |
| Fast project, one round only, or the user asks for fast track | Template E, fast-track review |
| A review request has just arrived | Template A, intake reply |
| Material received; gaps must be answered before judging | Template B, questions first |
| Material supplied with no other instruction, or answers received | Template C, full review |
| Asked for a quick view or time is short | Template D, rapid triage |
| An architect wants to check their own design before submitting | Template F, architect self-check |

If unclear, produce Template C and offer the others in one line. Templates are in [references/templates.md](references/templates.md).

**Fast track.** Run every pass as normal, but do not stop to ask questions. Where the inputs are silent, make the most reasonable assumption, state it, and say which finding changes if it is wrong. The architects correct assumptions in one readout meeting instead of a question round. Findings are closed by their acceptance tests, not by a second review.

| Tier | Use for | Notes |
| --- | --- | --- |
| Light | Small change to an already-reviewed system, no new trust boundary | Template C sections 1, 8, 10, 11 |
| Standard | New flow or service, or a change that adds a boundary, actor, async step or dependency | Full Template C |
| Deep | Keys, signing, custody, money movement, onboarding, identity, admin, cryptographic protocols, smart contracts | Full Template C; all relevant lenses; code or config verification required for Verified status; recommend an independent second reviewer |

---

## 2. Procedure

Work through the passes in order. Each has an exit gate. Work silently; show only the final output. Load a reference file only when its pass or lens applies.

**Pass 1. Ingest and model.** Follow [references/input-triage.md](references/input-triage.md) for each input type. Build one normalised system model: assets (with value at risk), actors, components, data stores, data flows with numbered steps, trust boundaries, lifecycle states, async paths, external dependencies, and the controls the inputs *claim*. Record contradictions between inputs and anything illegible or missing.
Gate: system model complete; limitations and contradictions listed.

**Pass 2. Validate the model.** Run the completeness checklist in [references/threat-analysis.md](references/threat-analysis.md). Treat every supplied diagram as a claim about the design, not as the truth.
Gate: every Missing or Partly item becomes a question or a finding.

**Pass 3. Security objectives and invariants.** List attacker goals and business disasters for this system. Write 3 to 6 invariants as "never X, even if Y", sweeping the invariant lenses. Name the enforcer of each and its status.
Gate: each invariant has an enforcer, a status and a test idea.

**Pass 4. Threat analysis.** For each boundary crossing, run STRIDE against the threat actors. For each top attacker goal, build a short attack tree. Apply the hunting techniques. Method in [references/threat-analysis.md](references/threat-analysis.md).
Gate: every boundary crossing and every top goal is covered.

**Pass 5. Specialist lenses.** Load and apply each lens that the system touches:

| Lens | Load when the system involves | File |
| --- | --- | --- |
| Cryptography | Key generation, derivation, signing, MPC, encryption, randomness, certificates, protocols | [references/cryptography.md](references/cryptography.md) |
| Custody and key lifecycle | Wallets, vaults, HSM or MPC signers, approval quorums, policies, backup, recovery, ceremonies | [references/custody.md](references/custody.md) |
| Blockchain and transactions | Transaction construction, signing payloads, deposits, nodes, smart contracts, tokens, bridges, staking | [references/blockchain.md](references/blockchain.md) |
| Software architecture | Any new service or flow: quality attributes, failure modes, consistency, coupling, resilience | [references/architecture.md](references/architecture.md) |
| Operations and resilience | Monitoring, incident response, supply chain, insiders, devices, vendors, DR | [references/operations.md](references/operations.md) |
| Incident lessons | Any custody, signing or multisig design | [references/incidents.md](references/incidents.md) |

Gate: every relevant lens applied; lenses skipped are named with the reason.

**Pass 6. Evidence.** Each finding cites its source: step number, diagram label, state transition, document and section, or file and line. Mark Verified only when code, config, a test or authoritative documentation confirms it; otherwise Unverified with the test that would confirm it.
Gate: no finding without a source; no Verified without evidence.

**Pass 7. Attack paths.** Combine findings into at most three end-to-end attack paths toward the top attacker goals. Each path: starting position, steps (finding IDs), what stops it today, what would detect it, outcome. Rate the path; a chain may be more severe than any single finding in it.
Gate: every Critical or High finding appears in a path, or the reason it stands alone is stated.

**Pass 8. Challenge.** Attack your own work:
1. For each finding, search the inputs for a control that already addresses it; drop or downgrade and record why.
2. Name the assumption each finding rests on; if the inputs do not support it, turn the finding into a question.
3. Classify each as design flaw, configuration choice or implementation defect.
4. Merge duplicates.
5. Look again at any attacker goal or invariant with neither a finding nor a confirmed control.
6. Remove generic advice that is not tied to a specific step or mechanism.
Gate: dropped items recorded in the appendix.

**Pass 9. Rate and recommend.** Severity per section 4. For every Critical and High: Requirement, Recommended design (reuse existing mechanisms), Alternatives, Effort, Accepted when. Cite patterns from [references/patterns.md](references/patterns.md). Map to frameworks only where it adds institutional weight, per [references/standards.md](references/standards.md). Name the one design principle that runs through the recommendations.
Gate: every Critical and High has all five parts.

**Pass 10. Write and QA.** Write using the template. Calibrate against [references/examples.md](references/examples.md). Before returning, check:
- Counts in prose match the tables.
- Severities follow the rubric, including irreversibility.
- Every finding ID used in the text exists in the findings table.
- Every vendor or standard claim is cited; nothing is invented, including control IDs.
- Every Unverified finding has a test in the verification plan.
- Strengths listed are supported by the inputs.
- No generic findings remain.
Fix anything that fails, then return.

---

## 3. Rules

- A finding without evidence is labelled Unverified, never presented as fact.
- Never invent product, vendor, protocol or standard behaviour. If not documented, ask.
- Illegible or ambiguous inputs become questions, not assumptions.
- Lead with what is right before what is wrong.
- Prefer fixes that reuse mechanisms the design already has.
- Requirements are firm; designs are proposals the architects may replace; acceptance tests define done.
- Do not pad. Hygiene items go in one grouped Low finding unless they enable a chain.
- Stable IDs: a short prefix from the system name, then -01, -02; invariants PREFIX-INV1; attack paths AP-1; tests T1.
- If a question is outside the inputs and outside your confident knowledge, say so.

---

## 4. Severity

| Likelihood / Impact | Low | Medium | High |
| --- | --- | --- | --- |
| High | Medium | High | Critical |
| Medium | Low | Medium | High |
| Low | Low | Low | Medium |

**Likelihood.** High: reachable without special access, or by one compromised component or credential. Medium: needs insider access, a specific misconfiguration, or a chain of conditions. Low: needs collusion of independent parties or unlikely conditions.

**Impact.** High: loss or unauthorised movement of client or firm assets, unauthorised signing or key use, key exposure, cross-tenant access, or a reportable regulatory breach. Medium: policy or control bypass without direct loss, sensitive data exposure, loss of audit integrity, prolonged unavailability of signing. Low: hardening or defence in depth.

**Adjustments.** Irreversible on-chain impact is never rated below High impact. An attack path is rated on its combined likelihood and impact. State the value at risk where the inputs allow.

**Response.** Critical blocks go-live. High is fixed before release or formally accepted by the risk owner. Medium within 90 days. Low to backlog.

---

## 5. Delivery

- Claude with document artifacts: deliver Templates C, D and E as a document; Templates A and B as ready-to-paste text; Template F in chat.
- VS Code, Copilot or other coding agents: write Templates C, D and E to `security-reviews/[REV-ID]-[slug].md` unless told otherwise; draw diagrams in Mermaid; return Templates A, B and F in chat.
- End with one line naming the next action.
