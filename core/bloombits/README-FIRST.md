# DASG Protocol Security Review for VS Code Copilot Chat

## What is in this folder

```
DASG-Security-Review-VSCode/
  README-FIRST.md                      <- this file
  VERIFICATION.md                     <- what was tested and the results
  install-windows.ps1                  <- Windows installer
  install-mac-linux.sh                 <- macOS / Linux installer
  skills/
    dasg-protocol-security-review/
      SKILL.md                         <- the review skill
      assets/review-tracker-template.xlsx
      references/withdrawal_auth.spthy <- tested Tamarin example
  agents/
    dasg-tamarin-modeller.md           <- writes and runs Tamarin proofs
    dasg-protocol-refuter.md           <- independently challenges the review
```

Copilot Chat finds these files only when they are in a folder named `.claude` in your home folder. The installer copies them there.

## 1. Install

### Option A: run the installer

**Windows:** open PowerShell in this folder and run:
```
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
```

**macOS / Linux:** open a terminal in this folder and run:
```
bash install-mac-linux.sh
```

The installer lists every file it copied.

### Option B: copy by hand (if scripts are blocked on your machine)

Windows, in Command Prompt:
```
mkdir %USERPROFILE%\.claude\skills
mkdir %USERPROFILE%\.claude\agents
xcopy /E /I /Y skills\dasg-protocol-security-review %USERPROFILE%\.claude\skills\dasg-protocol-security-review
copy /Y agents\*.md %USERPROFILE%\.claude\agents\
```

macOS / Linux:
```
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R skills/dasg-protocol-security-review ~/.claude/skills/
cp agents/*.md ~/.claude/agents/
```

### Then, in VS Code

1. Open the Command Palette (Ctrl+Shift+P, or Cmd+Shift+P on macOS) and run **Developer: Reload Window**.
2. Open Copilot Chat, switch to **Agent** mode, and choose a **Claude Opus** model.
3. Type `/`. The list should include `dasg-protocol-security-review`.
4. Open the agent picker. It should list `dasg-tamarin-modeller` and `dasg-protocol-refuter`.

Before you start, confirm that Copilot is approved for the classification of the documents you will review.

### Optional: Tamarin, for formal proofs

- macOS / Linux: `brew install tamarin-prover/tap/tamarin-prover`
- Windows: install WSL2 with Ubuntu, then run the same command inside it.

Without Tamarin everything still works. Proofs are reported as "Model written, not run" and properties are marked "Argued" instead of "Proved".

## 2. Use

Put the flow documents in your VS Code workspace folder. HTML, PDF, Markdown and diagram files all work. Paste these prompts in order, replacing the parts in [brackets].

**Step 1: run the review**
```
/dasg-protocol-security-review
Review the [withdrawal] flow in #[file name].
Profile: custody wallet. Evidence: design documents only (L1).
Scope: [list the flows]. Document version: [v1.0].
```
It works through Steps 0 to 6, lists open questions, and stops for sign-off.

**Step 2: answer the questions and sign off**
```
Answers from the architects: [paste answers].
Phase B is signed off. Specification confirmed by [name]; properties confirmed by [name];
adversary model agreed by [name]; date [date]. Continue with Phase C.
```

**Step 3: prove the critical property**
```
Use the dasg-tamarin-modeller agent on the [withdrawal] flow from this review.
Property: authorisation-to-signature binding on the exact signed digest.
Adversary: controls the coordinator and the network.
```

**Step 4: challenge the result**
```
Use the dasg-protocol-refuter agent.
Documents: #[file name]. Claims: [paste the Supported properties]. Do not use the rest of this review.
```

**Step 5: get the deliverables**
```
Produce the final review report and fill the tracker spreadsheet template. Save it as [name].xlsx.
```

## 3. Reading the results

- **Status:** Supported, Violated, Unverified, Out of scope, or Risk accepted.
- **Level:** L1 design, L2 code, L3 tested.
- **Evidence type:** Proved (tool output), Tested, Argued (reasoning checked by a named person), or Asserted (design claim only).

A critical property counts as proven only when its evidence type is Proved or Tested.

## 4. Troubleshooting

| Problem | Fix |
| --- | --- |
| Skill not in the `/` list | Check that `<home>/.claude/skills/dasg-protocol-security-review/SKILL.md` exists, then reload the window |
| Can't see the `.claude` folder | It is hidden. Windows: View > Show > Hidden items. macOS Finder: Cmd+Shift+. |
| Agents not listed | Check that `<home>/.claude/agents/` contains the two `dasg-` files, and that Copilot Chat is in Agent mode |
| PowerShell says scripts are disabled | Use Option B |
| "Tamarin not installed" | Run `tamarin-prover --version` in a terminal. If that works, start VS Code from that terminal with `code .` |
| Tamarin encoding error | Run `export LANG=C.UTF-8 LC_ALL=C.UTF-8` first |
| Review skips steps | Say: "Run every step in order and show each under its Step heading" |
