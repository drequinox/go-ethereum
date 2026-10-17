# Security Architecture Review Skill — VS Code Guide

## Overview

The **security-architecture-review** skill turns whatever material you have on a system (HTML design pages, diagrams, documents, API specs, vendor docs, code) into a finished security and software architecture review. It is specialised for digital asset custody, wallets, blockchain and cryptography, with chain-specific checks for Bitcoin, EVM chains and layer 2s, Solana, Cosmos, Aptos and Sui, XRPL, Stellar, Tron, TON and Polkadot, and a set of universal questions for any other chain. It works in GitHub Copilot in VS Code, and in Claude.

The default way of working is **fast track**: one review document, sent once, then one 30-minute readout. Instead of a question round, the review states its assumptions and what changes if each is wrong.

Every review also writes **workpapers** beside it: a coverage ledger with one row for every step of every flow, every lens check, the sources used, and what the independent passes added. The review stays short for the architects; the workpapers prove nothing was skipped. With the agents installed (step 6a), Deep-tier reviews run four specialists in parallel and an independent auditor automatically.

| Stage | What happens | Your time |
| --- | --- | --- |
| Setup, once | Install the skill and prepare a workspace | 15 minutes |
| Day 0 | Prepare inputs and run the review | 10 minutes |
| Day 0 | Check and edit the draft, then send it | 30–60 minutes |
| Day 1–2 | Readout with the architects | 30 minutes |
| After | Findings close when their tests pass in the team's own suite | None |

Throughout this guide, `REV-012` stands for your review ID. Replace it, and the context lines in the prompts, with your own.

## Part 1: One-time setup

### Step 1. Prerequisites

- Update VS Code to the latest version.
- Install the **GitHub Copilot Chat** extension and sign in.
- Confirm your firm approves Copilot for architecture material, and which models you may use.

### Step 2. Install the skill

Download `security-architecture-review.zip`. If an older version is installed, delete the old `security-architecture-review` folder (and any `flow-security-review` folder) first.

macOS or Linux:

```bash
mkdir -p ~/.copilot/skills
unzip ~/Downloads/security-architecture-review.zip -d ~/.copilot/skills/
ls ~/.copilot/skills/security-architecture-review
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.copilot\skills"
Expand-Archive "$HOME\Downloads\security-architecture-review.zip" -DestinationPath "$HOME\.copilot\skills" -Force
dir "$HOME\.copilot\skills\security-architecture-review"
```

The listing should show `SKILL.md`, `README.md`, `USER-GUIDE.md`, `context-template.md`, `agents`, `references`, `scripts` and `evals`. Do not rename the folder; its name must match the skill.

To share the skill with a team through a repository instead, copy the folder to `.github/skills/security-architecture-review/` in that repository.

### Step 3. Reload VS Code

Press Ctrl+Shift+P (Cmd+Shift+P on Mac) and run **Developer: Reload Window**. If the skill is not found later, open Settings, search "skills" and make sure Agent Skills is enabled; early builds treated it as experimental.

### Step 4. Confirm Copilot can see it

Open Copilot Chat (Ctrl+Alt+I), switch the mode picker to **Agent**, and send:

```text
Do you have the security-architecture-review skill? List its seven modes.
```

It should list fast track, intake reply, questions first, full review, rapid triage, architect self-check and coverage audit.

### Step 5. Optional extras

- **Markdown Preview Mermaid Support** (from the Extensions view), so diagrams in reviews render in the preview.
- **Playwright**, for one-command extraction of diagrams from HTML pages. Skip it if your laptop does not allow installs; there is a no-install alternative in Part 2.

```bash
pip install playwright
playwright install chromium
```

### Step 6. Create a reviews workspace

```text
security-reviews/
  REV-012/
    inputs/
```

Open the `security-reviews` folder in VS Code (File, Open Folder). One subfolder per review keeps each review with its inputs.

### Step 6a. Recommended: add the review agents

The skill works on its own when you name it in a prompt. The agents add the strongest defence against misses: independent passes. With them, a Deep-tier review runs four specialists in parallel, each in its own context (keys, cryptography and custody; chains and transactions; identity, API and data; architecture and operations). An independent auditor then checks the finished review. You still send one prompt. Install all three agent files:

macOS or Linux:

```bash
mkdir -p ~/.copilot/agents
cp ~/.copilot/skills/security-architecture-review/agents/*.agent.md ~/.copilot/agents/
```

Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force "$HOME\.copilot\agents"
Copy-Item "$HOME\.copilot\skills\security-architecture-review\agents\*.agent.md" "$HOME\.copilot\agents\"
```

| Agent | In the dropdown | What it does |
| --- | --- | --- |
| Security Reviewer | Yes | The lead: models the design, runs the specialists and the auditor, writes the review and its workpapers |
| Review Specialist | No (helper) | Applies one group of lenses in its own context and reports back |
| Coverage Auditor | Yes | Audits a finished review against its inputs and reports only gaps |

For the most independent audit, open `~/.copilot/agents/coverage-auditor.agent.md` and add a line `model: <name>` to its frontmatter, naming an approved model different from the one you review with, exactly as it appears in the model picker. Subagents use more requests than a single pass.

Reload VS Code. Pick **Security Reviewer** from the agent dropdown, then a short prompt is enough:

```text
Review REV-012/inputs. Context: custody platform, client assets at risk.
```

Each review produces two files: `review.md` for the architects, and `review-workpapers.md`, which proves coverage (every step of every flow, every lens check, sources, and what the independent passes added). After each review, buttons offer: audit coverage (different model), challenge the findings, draft the cover email, apply readout notes. Every prompt in Part 3 also works with this agent selected.

### Step 6b. Write your standing context once

Context tells the review what is at stake, so it can rate severity and choose depth. It does not limit which risks are considered. Instead of typing it in every prompt, save it as a file:

```bash
cp ~/.copilot/skills/security-architecture-review/context-template.md security-reviews/context.md
```

On Windows: `Copy-Item "$HOME\.copilot\skills\security-architecture-review\context-template.md" security-reviews\context.md`

Fill it in: system, users, value at risk, key management, vendors, regulation, out of scope, go-live. `security-reviews/context.md` applies to every review. A `context.md` inside a review folder adds to or overrides it for that review. Anything in the prompt overrides both. With context saved, the "Context:" line in the prompts below becomes optional.

## Part 2: Preparing inputs

Put everything for the review in `REV-012/inputs/`: HTML pages, images, Markdown, API specs, vendor documents, notes. Then prepare by type.

| Input | What to do |
| --- | --- |
| HTML design pages | Steps 7 and 8 below |
| Diagram images or screenshots | Use as they are; make sure every label is readable at full size |
| Word documents | Convert with pandoc: `pandoc design.docx -t gfm -o inputs/design.md --extract-media=inputs/media` |
| PDF documents | Export the text, and save each diagram as a PNG |
| Markdown, Mermaid, OpenAPI, code | Use as they are |

Open the VS Code terminal (Ctrl and the backtick key) for the commands below. On Windows, use `python` instead of `python3`, and `$HOME\.copilot\skills\...` in paths.

### Step 7. Convert HTML pages to clean text

```bash
python3 ~/.copilot/skills/security-architecture-review/scripts/html_to_review.py REV-012/inputs/*.html
```

Each page produces `<page>.review.md`: headings, text, tables and code, with collapsed sections expanded, SVG diagram labels listed, and embedded images saved to `<page>_media/`. Page styling and scripts are removed.

### Step 8. Extract the diagrams

Text conversion keeps diagram labels but not the arrows. To reconstruct each diagram as "from -> to : label", use **one** of these.

**With Playwright** (all pages in one command):

```bash
python3 ~/.copilot/skills/security-architecture-review/scripts/extract_diagrams.py REV-012/inputs/*.html
```

Each page produces `<page>.diagrams.md` and a screenshot of every diagram in `<page>_diagrams/`.

**Without installing anything** (per page):

1. Open the page in Chrome or Edge and press F12. Go to the Console.
2. Paste the whole contents of `scripts/diagram_extract.js` and press Enter.
3. Run `extractAllDiagrams()`. The result is copied to your clipboard.
4. Paste it into `REV-012/inputs/<page>.diagrams.md`.
5. Screenshot each diagram into `REV-012/inputs/`.

If a diagram is missed, select it in the Elements panel and run `extractDiagram($0)`.

**Check before running the review** (one minute per page): open each `.diagrams.md` and compare it with the screenshot. Anything listed as unresolved or "direction unknown" stays for the review to check against the picture. Diagrams drawn on a canvas cannot be extracted; the screenshot is the input.

## Part 3: Prompt library

Before any prompt: open Copilot Chat, select **Agent** mode and your strongest approved model. Drag diagram screenshots into the chat, or reference files with `#file:`. Approve file reads and writes when Copilot asks.

Every prompt names the skill, points at the inputs, says which output you want, and gives context. Context (what the system is, what is at stake) is what makes findings specific rather than generic.

### Everyday: fast track of all flows

**1. Default review.** Use this for most reviews.

```text
Run security-architecture-review on everything in REV-012/inputs (use the .review.md, .diagrams.md and screenshots). Fast track, Deep tier. Context: institutional custody platform, client assets at risk. Review every flow you find. Start with a list of the flows found and the tier applied to each. Write to REV-012/review.md.
```

### Large documents (more than about five flows)

One pass over many flows gets thinner on each. Inventory first, then review in batches, highest risk first.

**2. Inventory the flows.**

```text
Using security-architecture-review, list every flow in REV-012/inputs with a one-line description, what it touches (keys, money, identity, admin) and the tier you would apply. Do not review yet.
```

**3. Review the high-risk flows.**

```text
Now review the Deep-tier flows from that list. Fast track. Write to REV-012/review-part1.md.
```

**4. Review the rest.**

```text
Now review the remaining flows from that list at the Light tier. Fast track. Write to REV-012/review-part2.md.
```

### Controlling scope

**5. One flow only.**

```text
Run security-architecture-review on the withdrawal flow in REV-012/inputs only; ignore the other flows. Fast track, Deep tier. Write to REV-012/review-withdrawal.md.
```

**6. Exclude flows already reviewed.**

```text
Run security-architecture-review on everything in REV-012/inputs except tenant onboarding, which was reviewed in REV-009. Fast track, Deep tier. Write to REV-012/review.md.
```

**7. Set priorities.**

```text
Run security-architecture-review on everything in REV-012/inputs. Fast track. Go deepest on withdrawal and key rotation; Light tier for reporting flows. Write to REV-012/review.md.
```

### Other output modes

**8. Full review** (for major designs, audits or when time allows).

```text
Run security-architecture-review on everything in REV-012/inputs. Full review (Template C), Deep tier. Context: institutional custody platform, client assets at risk. Include attack paths and the architecture assessment. Write to REV-012/review-full.md.
```

**9. Rapid triage** (a one-page pre-read).

```text
Run security-architecture-review on REV-012/inputs. Rapid triage: top risks, most likely attack path, and the questions that would change the verdict.
```

**10. Intake reply** (if you want to acknowledge formally before reviewing).

```text
Using security-architecture-review, produce the intake reply for REV-012, Deep tier, response due 31 October, addressed to Sarah, lead architect.
```

**11. Questions first** (when the design is too incomplete to judge).

```text
Run security-architecture-review on REV-012/inputs. Questions first: only questions arising from gaps in the flows, grouped, each tagged with what it would close. Flag anything illegible.
```

**12. Vendor integration.**

```text
Run security-architecture-review on REV-012/inputs from the integrator's perspective. The vendor documentation is in vendor-docs.md. Build the shared-responsibility table, answer the vendor questions in the skill's design-principles reference from the vendor's documentation, and cite the vendor documentation for every vendor claim. Fast track, Deep tier. Write to REV-012/review.md.
```

**12a. Compare a design with industry practice** (to strengthen recommendations, not to set the standard).

```text
Using security-architecture-review, assess REV-012/review.md and its inputs against the custody design principles (DP-1 to DP-13). For each principle, say whether the design meets it and, where useful, how documented platforms implement it, with links. Principles decide; the industry comparison is supporting evidence only. Add one industry comparison line to each recommendation where it helps.
```

### While editing the draft

**13. Challenge a finding.**

```text
Challenge findings TO-02 and TO-05: what in the inputs could already address them? Downgrade or withdraw them if the evidence does not hold.
```

**14. Find the cheapest proof.**

```text
Which findings are Unverified, and what is the cheapest test for each?
```

**15. Re-rate for value at risk.**

```text
Re-rate the findings assuming the platform will hold 500 million in client assets. Explain any change.
```

**16. Explain a finding to engineers.**

```text
Explain finding TO-04 to the engineering team in five sentences, with the attack in plain words and the fix.
```

**17. Draft the cover note.**

```text
Draft a two-paragraph email to the architects sending REV-012/review.md and proposing a 30-minute readout this week.
```

### After the readout

**18. Apply the readout outcomes.**

```text
Update REV-012/review.md using REV-012/inputs/readout-notes.md: withdraw or re-rate findings affected by corrected assumptions, and list final conditions with owners and dates.
```

**19. Apply the architects' answers** (if you used questions first).

```text
The architects' answers are in REV-012/inputs/answers.md. Re-run security-architecture-review on all inputs including the answers. Fast track. Close or confirm each point and write to REV-012/review.md.
```

**20. Review a changed design.**

```text
The design has changed; the new version is in REV-012/inputs-v2. Run security-architecture-review on the changes only, against REV-012/review.md. Fast track. Say which findings are closed, which remain, and anything new. Write to REV-012/review-v2.md.
```

### Catching misses

**21. Coverage audit.** Open a new chat, pick **Coverage Auditor** in the agent dropdown if you installed it, and choose a different model from the one that wrote the review if you can.

```text
Run security-architecture-review in coverage audit mode on REV-012/review.md against everything in REV-012/inputs. Rebuild the flows, boundary crossings and attacker goals from the inputs before reading the review, then report only gaps.
```

**22. Fold the audit into the review.** Back in the original chat, or any chat:

```text
Update REV-012/review.md using REV-012/review-audit.md: add the missed risks as findings, correct the unsupported claims, and close the coverage gaps. Keep the existing finding IDs.
```

**23. Record a miss found later.**

```text
A pen test found [what was missed] in the REV-012 design. Help me record it in the skill's evals/misses-log.md, and propose the golden case and the checklist item that would have caught it.
```

## Part 4: Checking, sending and closing a review

### Step 9. Check the draft (30–60 minutes)

Open `REV-012/review.md` (and `REV-012/review-workpapers.md` beside it) and press Ctrl+Shift+V for the preview. The skill drafts; you decide what goes out. Check:

- [ ] The list of flows found matches the document; nothing is missing.
- [ ] Every finding points to a real step, label or section in the inputs.
- [ ] Assumptions are reasonable; correct any you already know the answer to.
- [ ] Severities fit what is actually at stake.
- [ ] Nothing generic remains (advice not tied to a specific step).
- [ ] Unverified findings are labelled as such.
- [ ] The coverage line shows the independent passes ran. In the workpapers, skim the ledger's Unknown cells: answer any you already know.

Use prompts 13 to 16 to tighten anything that is weak.

For Deep-tier reviews, also run the coverage audit on a **different model** before sending: the **Audit coverage (different model)** button, or prompt 21 in a **new chat**, then prompt 22 to fold the gaps in. The built-in auditor runs on the same model unless you set one; a different model does not share the first one's blind spots.

### Step 10. Send it

Send `review.md`. Keep `review-workpapers.md` on file as the evidence of coverage; share it only with a second reviewer, an auditor, or architects who ask. Share the review as it is, or convert it for email:

```bash
pandoc REV-012/review.md -o REV-012-review.docx
```

pandoc does not draw Mermaid diagrams; copy those from the VS Code preview as images. Prompt 17 drafts the cover note.

### Step 11. Hold the readout (30 minutes)

| Minutes | Agenda |
| --- | --- |
| 10 | Correct the review's assumptions |
| 15 | Agree owners and dates for each condition |
| 5 | Record any risk acceptances, with the risk owner |

For flows that move money or touch keys, keep the readout even under time pressure; fast track depends on it to catch wrong assumptions.

### Step 12. Close it out

Save what was agreed to `REV-012/inputs/readout-notes.md`, then run prompt 18. From then on, each finding closes when its "done when" test passes in the team's own test suite. No second review is needed unless the design changes; if it does, use prompt 20.

## Part 5: Architect self-check and validating the skill

### Step 13. Let architects check their own designs first

The biggest time saver: architects fix the obvious gaps before the design reaches you. Copy the skill folder into their repository at `.github/skills/security-architecture-review/`. Before submitting a design, they run:

```text
Run security-architecture-review on my design in docs/design. Architect self-check (Template F).
```

They get completeness gaps, the findings a security review would likely raise with the recommended fix patterns, and the assumptions to state explicitly. Your review then starts from a cleaner design.

### Step 14. Validate the skill before your first live review

A skill is only as good as its results with your tool and model. Do this once, and again after changing model or updating the skill.

1. Open `~/.copilot/skills/security-architecture-review/evals/golden-cases.md`.
2. For each of the six cases, start a fresh chat, paste only the case's input, and send:

```text
Run the security-architecture-review skill on this. Produce the full review.
```

3. Compare with the expected findings in the file. Run each case three times.
4. Record results in the log at the bottom of the file.

| Measure | Target before relying on it |
| --- | --- |
| High findings found | 80% or more |
| All findings found | 60% or more |
| Findings you agree are real | 80% or more |
| Invented facts | None |
| High findings found in all three runs | 80% or more |

### Step 15. Keep a misses log

When anything the review missed turns up later (from a coverage audit, an architect, a pen test or an incident), record it with prompt 23 in `evals/misses-log.md`, add it to the golden cases, and add the check that would have caught it. This is how the skill gets better with every review rather than staying as good as the day it was installed.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| The skill is not used | Use Agent mode, name the skill in the prompt, check the folder path and name, reload the window |
| Review lacks cryptography, custody or architecture depth | The `references` folder is missing or moved; reinstall the full zip |
| A flow in the document was skipped | Check the flow list at the top of the review; use prompt 2 to inventory, then prompt 5 for the missed flow |
| Findings are generic | Add context: what the system is, what is at stake, which flows matter most |
| HTML diagrams have labels but no arrows | Run the diagram extractor (step 8); text conversion alone cannot capture arrows |
| Connectors listed as unresolved | Check them against the screenshot; the review flags them too |
| A diagram has nothing to extract | It is drawn on a canvas; use a screenshot |
| Results differ between runs | Normal for AI models; use the strongest approved model and compare against the golden cases |
| The coverage line says the independent passes did not run | Install all three agent files (step 6a), update VS Code, and select **Security Reviewer**; a model the auditor names above your current model's cost tier is refused, so pick one at or below it |
| Copilot cannot read a Word or PDF file | Convert to Markdown (Part 2) and attach diagrams as images |
| Claims marked "not verified against current sources" | Copilot had no web access. If your firm allows it, enable Copilot's web fetch tool and re-run; otherwise check those claims yourself or leave them in the verification plan |

## Quick reference

**Install once:** unzip to `~/.copilot/skills/`, copy the three files in `agents/` to `~/.copilot/agents/`, optionally set a different `model:` in the Coverage Auditor, reload VS Code, confirm in Agent mode.

**Each review:**

1. Inputs into `REV-012/inputs/`.
2. HTML pages: run `html_to_review.py`, then `extract_diagrams.py` or the Console method.
3. Prompt 1 (or prompts 2–4 for large documents).
4. Check the draft and the coverage line against the checklist in step 9; for Deep-tier reviews, run the coverage audit on a different model (the button, or prompts 21 and 22).
5. Send, hold the 30-minute readout, run prompt 18.
6. Findings close when their tests pass.

**The default prompt:**

```text
Run security-architecture-review on everything in REV-012/inputs (use the .review.md, .diagrams.md and screenshots). Fast track, Deep tier. Context: [what the system is, what is at stake]. Review every flow you find. Start with a list of the flows found and the tier applied to each. Write to REV-012/review.md.
```

**Rules that keep reviews trustworthy:** confidential material only in approved tools; nothing unverified presented as fact; you sign what goes out.
