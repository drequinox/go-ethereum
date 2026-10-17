# security-architecture-review skill

Full security and software architecture review from any inputs (diagrams, images, documents, API specs, vendor docs, code, IaC), specialised for digital asset custody, wallets, blockchain and cryptography. Follows the open Agent Skills format, so the same folder works in Claude, VS Code Copilot, Copilot CLI and other compatible tools.

## Structure

```
security-architecture-review/
  SKILL.md                     core procedure, modes, severity, rules (always loaded)
  references/
    input-triage.md            how to read each input type; the system model
    threat-analysis.md         completeness, attacker goals, invariants, STRIDE, attack trees, techniques, attack paths
    cryptography.md            randomness, signatures, MPC, derivation, binding, backups, authentication, post-quantum
    custody.md                 tiers, signer-enforced policy, quorum independence, blind signing, withdrawals, ceremonies, recovery
    blockchain.md              transactions, deposits and finality, addresses, smart contracts, bridges, staking, compliance
    architecture.md            quality attribute scenarios, consistency, failure modes, coupling (ATAM-light)
    operations.md              detection, response, people, devices, supply chain, continuity
    incidents.md               lessons from real custody and bridge losses, mapped to checks
    standards.md               framework mapping, with a rule against invented control IDs
    patterns.md                22 recommendation patterns with acceptance tests
    templates.md               fast track, intake, questions, full review, rapid triage, architect self-check
    examples.md                calibration: good and bad findings, attack paths, dropped items
  evals/
    golden-cases.md            four golden cases with expected findings and traps
```

Reference files load only when their pass or lens applies, which keeps the model's attention on the material.

## Install

**VS Code (GitHub Copilot)**
- One repository: copy the folder to `.github/skills/security-architecture-review/`.
- All your workspaces: copy it to `~/.copilot/skills/security-architecture-review/`.
- VS Code also reads `.claude/skills/` and `~/.claude/skills/`.
- Use Agent mode and the strongest reasoning model your organisation approves.
- Ask: "Run security-architecture-review on these" and attach the diagrams, documents or code.

**Claude Code**: copy the folder to `~/.claude/skills/` or the project's `.claude/skills/`.

**Claude**: add the folder (or this zip) as a skill. Keep the `references` folder with SKILL.md; the skill depends on it.

If you installed the earlier `flow-security-review` skill, remove it so the two do not compete for the same requests.

## Before trusting it

Run the four cases in `evals/golden-cases.md` in your target tool and model, three times each, and record recall, precision, fabrications and consistency. Re-run after any change to the skill or the model.

## Data handling

Architecture material, code and configuration are confidential. Use the skill only in tools and with models your organisation has approved for that material.
