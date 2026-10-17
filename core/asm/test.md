Here's the complete guide for the final version, updated for fast track and HTML inputs. Allow 15 minutes for the one-time setup and about an hour of your time per review.

## Part 1: One-time setup

**1. Prerequisites**
- Update VS Code to the latest version.
- Install the **GitHub Copilot Chat** extension and sign in.
- Confirm that your firm approves Copilot for architecture material, and note which models you may use.

**2. Install the skill**

Download `security-architecture-review.zip`. If an older version is installed, delete the old `security-architecture-review` folder, and any `flow-security-review` folder, first.

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

You should see `SKILL.md`, `README.md`, `references`, `scripts` and `evals`. Don't rename the folder.

**3. Reload VS Code**

Press Ctrl+Shift+P (Cmd+Shift+P on a Mac) and run **Developer: Reload Window**. If skills don't appear later, open Settings, search "skills" and make sure Agent Skills is enabled.

**4. Confirm Copilot sees the skill**

Open Copilot Chat (Ctrl+Alt+I), select **Agent** mode, and ask:
```
Do you have the security-architecture-review skill? List its six modes.
```
It should list fast track, intake, questions, full review, rapid triage and architect self-check.

**5. Optional extras**
- **Markdown Preview Mermaid Support** extension, so the review's diagrams render.
- **Playwright**, for batch extraction of HTML diagrams. Skip it if your laptop blocks installs; the browser Console method needs nothing.
  ```bash
  pip install playwright
  playwright install chromium
  ```

**6. Create your reviews workspace**
```
security-reviews/
  REV-012-custody-flows/
    inputs/
```
Open `security-reviews` with File → Open Folder.

## Part 2: Each review (fast track)

**7. Put the inputs in `inputs/`**

HTML pages, images, Markdown, specs: anything goes.

**8. Prepare HTML pages** (skip this step if you have none)

Open the VS Code terminal (Ctrl+`) and convert the text:
```bash
python3 ~/.copilot/skills/security-architecture-review/scripts/html_to_review.py REV-012-custody-flows/inputs/*.html
```

Then extract the diagrams, using **one** of these:
- **With Playwright:**
  ```bash
  python3 ~/.copilot/skills/security-architecture-review/scripts/extract_diagrams.py REV-012-custody-flows/inputs/*.html
  ```
- **Without installing anything:** open each page in Chrome or Edge, press F12 and go to the Console. Paste in the contents of `scripts/diagram_extract.js`, press Enter, then run `extractAllDiagrams()`. Paste the result (now on your clipboard) into `inputs/<page>.diagrams.md`, and screenshot each diagram into `inputs/`.

On Windows, use `python` instead of `python3`, and `$HOME\.copilot\skills\...` in the paths.

Spend a minute opening the `.diagrams.md` files: do the connections match the pictures?

**9. Run the review**

In Copilot Chat, select **Agent** mode and your strongest approved model, then send:
```
Run security-architecture-review on everything in REV-012-custody-flows/inputs (use the .review.md, .diagrams.md and screenshots). Fast track (Template E), Deep tier. Context: institutional custody platform, client assets at risk; flows in scope: tenant onboarding, create wallet, withdrawal. Write to REV-012-custody-flows/review.md.
```
Approve the file reads and the file write when Copilot asks.

**10. Edit the draft (30–60 minutes)**

Open `review.md` and press Ctrl+Shift+V for the preview. Check that:
- every finding points to a real step or label,
- the assumptions are sensible (fix any you already know the answer to),
- the severities fit what's at stake,
- nothing generic remains.

Tighten it in the same chat if needed:
```
Challenge findings TO-02 and TO-05: what in the inputs could already address them?
```

**11. Send it and hold the readout**

Share `review.md`, or convert it to Word:
```bash
pandoc REV-012-custody-flows/review.md -o REV-012-review.docx
```
pandoc doesn't render Mermaid, so copy those diagrams from the preview as images.

Hold one 30-minute readout:
- 10 minutes to correct assumptions,
- 15 minutes to agree owners and dates,
- 5 minutes for any risk acceptances.

**12. Close it out**

Save the readout outcomes to `inputs/readout-notes.md`, then run:
```
Update REV-012-custody-flows/review.md using inputs/readout-notes.md: withdraw or re-rate findings affected by corrected assumptions; list final conditions with owners and dates.
```
From here, findings close when their "done when" tests pass in the team's own test suite. No second review is needed unless the design changes.

## Part 3: Worth doing once

**13. Let architects check their own designs first.** Copy the skill folder into their repository at `.github/skills/security-architecture-review/`. They run:
```
Run security-architecture-review on my design. Architect self-check (Template F).
```

**14. Validate before your first live review.** Run the four cases in `evals/golden-cases.md` in VS Code with your chosen model, each in a fresh chat. Compare against the expected findings and record the scores in the results log.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| The skill isn't used | Use Agent mode, name the skill in the prompt, check the folder path, reload the window |
| Shallow on crypto, custody or architecture | The `references` folder is missing; reinstall the full zip |
| Findings are generic | Add context: what the system is, what's at stake, which flows |
| HTML arrows are missing | Run the diagram extractor (step 8); text conversion alone can't capture arrows |
| Unresolved connectors in `.diagrams.md` | Check them against the screenshot; the review will flag them too |
| Canvas-drawn diagram | Nothing to extract; screenshot it |
| Results vary between runs | Normal; use the strongest model and compare against the golden cases |
