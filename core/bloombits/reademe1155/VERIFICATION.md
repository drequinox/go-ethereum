# Verification record

Package: DASG Security Review for VS Code Copilot Chat, version 1.1.0, built 20 October 2026.

## Format checks (all passed)

| Check | Result |
| --- | --- |
| Skill name `dasg-protocol-security-review` matches its folder and uses only a-z, 0-9 and hyphens, 64 characters max | Pass |
| Skill description is 1,024 characters or fewer (actual: 238) | Pass |
| Frontmatter starts on line 1 and parses as valid YAML, in all 3 files | Pass |
| Agent names match their file names | Pass |
| Agent tool lists use valid tool names; model is a valid value (`opus`) | Pass |
| Files referenced by the skill exist (`references/withdrawal_auth.spthy`, `assets/review-tracker-template.xlsx`) | Pass |
| `claude plugin validate --strict` | Pass |

## Functional tests (all passed)

| Test | Expected | Observed |
| --- | --- | --- |
| Skill on a sample withdrawal flow | Runs Steps 0 to 6, cites sources, stops at the Phase B gate | Stopped at the gate with a sign-off table; cited a document line for each protocol fact; flagged the approver signing an opaque digest |
| Tamarin template, signer without approval check | Property falsified | Falsified (substitution attack, 3 steps) |
| Tamarin template, signer with check and replay cache | Property verified | Verified (8 steps) |
| Tamarin template, check without replay cache (mutation) | Property falsified | Falsified (replay attack, 9 steps) |
| Modeller agent, live run | Writes a model, runs Tamarin, performs a mutation check, does not overclaim | Did all four; its reported results were independently re-run and matched exactly |
| Refuter agent, live run with one overclaimed claim | Refutes the overclaim, ignores supplied analysis | Refuted the replay-vulnerable claim; flagged a missing assumption in the proved claim; ignored the supplied analysis; labelled its own unconfirmed trace as a hypothesis |
| Tracker template recalculation | Zero formula errors | Zero errors; the evidence-type warning flagged a test row correctly |
| Installers (bash and PowerShell 7.5.3), from a clean home folder, run twice | All five files installed, no duplicates | Pass |

Tools used: Tamarin Prover 1.12.0, Maude 3.2, PowerShell 7.5.3.

## Not verified here

Loading inside VS Code Copilot Chat itself was not tested in this environment. The file layout follows the VS Code Agent Skills and custom-agent documentation for `~/.claude/skills/` and `~/.claude/agents/`. The `/` list and agent-picker checks in README-FIRST.md confirm loading on your machine.
