# security-architecture-review skill

Full security and software architecture review from any inputs (diagrams, images, documents, API specs, vendor docs, code, IaC), specialised for digital asset custody, wallets, blockchain and cryptography. Follows the open Agent Skills format, so the same folder works in Claude, VS Code Copilot, Copilot CLI and other compatible tools.

## Structure

```
security-architecture-review/
  SKILL.md                     core procedure, modes, severity, rules (always loaded)
  USER-GUIDE.md                installation and usage in VS Code, with the full prompt library
  context-template.md          standing review context: copy to context.md in your reviews workspace
  agents/
    security-reviewer.agent.md optional VS Code agent: copy to ~/.copilot/agents/ to get "Security Reviewer" in the agent dropdown
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
  scripts/
    html_to_review.py          converts HTML design pages into clean text inputs (standard library only)
    extract_diagrams.py        renders HTML pages and reconstructs each diagram as boxes and connections, with screenshots (needs Playwright)
    diagram_extract.js         the same extraction, pasted into the Chrome or Edge Console (no installation)
  evals/
    golden-cases.md            four golden cases with expected findings and traps
```

## HTML inputs

Convert HTML design pages before a review. The script keeps text, tables and code, expands collapsed sections, extracts the labels of every inline SVG diagram, keeps Mermaid source, and saves embedded images as files:

```
python3 ~/.copilot/skills/security-architecture-review/scripts/html_to_review.py inputs/*.html
```

Each page produces `<name>.review.md` next to it (and `<name>_media/` for embedded images).

Diagrams drawn in HTML and CSS (boxes and CSS-line arrows) need a browser to reconstruct the arrows. Either:

- **With Playwright** (`pip install playwright` then `playwright install chromium`):
  ```
  python3 ~/.copilot/skills/security-architecture-review/scripts/extract_diagrams.py inputs/*.html
  ```
  Each page produces `<name>.diagrams.md` (every diagram as "from -> to : label", with step numbers and direction) and `<name>_diagrams/diagram-N.png`.
- **Without installing anything**: open the page in Chrome or Edge, press F12, paste the contents of `scripts/diagram_extract.js` into the Console, press Enter, then run `extractAllDiagrams()`. The result is copied to your clipboard; paste it into `inputs/<name>.diagrams.md` and screenshot each diagram yourself. To extract one diagram, select it in the Elements panel and run `extractDiagram($0)`.

Give the review the `.review.md`, `.diagrams.md` and screenshots together. Anything the extractor lists as unresolved is checked against the screenshot. Canvas-drawn diagrams have nothing to extract; use the screenshot.

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
