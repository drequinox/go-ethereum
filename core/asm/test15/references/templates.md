# Output templates

Keep the section order fixed so readers learn where to look. Replace everything in square brackets.

## Template A: intake reply

Subject: Security review [REV-ID]: [system or flow name], received

Hi [name],

Thanks for sending [system or flow name]. We have logged it as [REV-ID], reviewed at the [Light / Standard / Deep] tier, with our response due by [date].

To start, please send whatever you have of the following. Anything missing will be listed as a limitation of the review, not held against the design.

1. Sequence and state diagrams for the flows in scope
2. Architecture overview: components, data stores, hosting, vendors
3. API specifications for the endpoints involved
4. For each step: which identity calls it, and how it is authenticated
5. Where data is written, and which identities can change it
6. Asynchronous parts: queues, events, webhooks, batch jobs
7. Failure, timeout and retry behaviour
8. Key management: where keys are generated, stored, backed up, and who can use them
9. Earlier reviews, accepted risks, and what has changed since

Within two working days we will send clarifying questions. Our review will then give a verdict, findings, attack paths and recommendations. Each recommendation has three parts: the requirement that must hold, a recommended design you are free to replace, and an acceptance test that defines done.

Could the tech lead spare 30 minutes in [week] to walk us through the design?

Thanks,
[Your name]

## Template B: questions first

Subject: [REV-ID] [name]: questions before our review

Hi [name],

We have checked the material for completeness. It covers [what it covers well, in one line]. Your answers will close or confirm several points before we write the review; a reply by [date] would help.

**Root of trust and approval**
1. [question] (closes [finding or gap])

**Keys and signing**
2. [question]

**Lifecycle and failure**
3. [question]

**Data, isolation and vendors**
4. [question]

**Clarifications**
5. [anything contradictory, ambiguous or illegible]

Thanks,
[Your name]

Only include questions that arose from the completeness check, the hunt or a lens. No generic questions.

## Template C: full review

### 1. Summary
**Verdict:** [OK / OK with conditions / Redesign]
[One paragraph: the single most important insight, in plain language.]
Blocking findings:
1. **[ID]:** [one line]
Top attack path: [AP-1 in one line].

### 2. Scope, inputs and limitations
| Field | Entry |
| --- | --- |
| System and flows in scope | |
| Out of scope | |
| Tier | |
| Inputs reviewed | |
| Verification performed | [code, config, tests, or none] |
| Limitations | [missing, contradictory or illegible inputs] |

### 3. System model
[Condensed model: assets with value at risk, actors, trust boundaries. Then the annotated flow: the architects' diagram redrawn, or Mermaid, with findings marked on steps or transitions and missing paths dashed.]

### 4. What the design gets right
- **[Strength]:** [the failure it prevents]

### 5. Completeness check
| Item | Yes / Partly / Missing | Gap and finding ID |
| --- | --- | --- |

### 6. Security objectives and invariants
Attacker goals considered: [list].
| ID | Invariant: never X, even if Y | Enforced by | Status |
| --- | --- | --- | --- |

### 7. Attack paths
**AP-1: [goal].** Starting position: [actor and access]. Steps: [finding IDs]. Stopped today by: [control or nothing]. Detected by: [signal or nothing]. Outcome: [asset, value at risk]. Severity: [rating].

### 8. Findings
| ID | Finding | Category | Severity | L × I | Source and evidence | Short fix |
| --- | --- | --- | --- | --- | --- | --- |
Category: design flaw, configuration, implementation, operational, architecture risk. Evidence: Verified with link, or Unverified.

### 9. Architecture assessment
| Quality attribute scenario | Met / Missed / Unknown | Note |
| --- | --- | --- |
Sensitivity points and trade-offs: [short list].

### 10. Verification plan
| Test | Steps | Expected if safe | Confirms |
| --- | --- | --- | --- |
Questions for vendors, numbered, where relevant.

### 11. Recommendations
Requirements are firm; designs are proposals you may replace; acceptance tests define done. Design principle: [one line].

**R1. [Title] ([finding IDs], [pattern IDs])**
- **Requirement:**
- **Recommended design:**
- **Alternatives:**
- **Effort:**
- **Accepted when:**

| Finding | Recommended fix | Accepted when |
| --- | --- | --- |

### 12. Target state
[The architects' diagram with recommendations applied, new or changed controls highlighted.]

### 13. Next steps and sign-off
| Condition | Owner | Due | Status |
| --- | --- | --- | --- |
Readout: [date]. Risk acceptances: [finding, accepted by, review date]. Framework mapping, if useful: [appendix].

| Role | Name | Decision | Date |
| --- | --- | --- | --- |
| Security reviewer | | | |
| Architecture owner | | | |
| Risk owner | | | |

Appendix: items dropped in the challenge pass, with the reason.

## Template D: rapid triage

One page, for a quick view or a pre-read:
1. **Verdict so far** and confidence (low, medium, high) given the inputs.
2. **Top risks**, at most five, each with source and severity.
3. **Most likely attack path**, in three lines.
4. **Questions that would change the verdict**, at most five.
5. **Recommended next step**: full review, targeted verification, or proceed.

## Template E: fast-track review

One document, sent once, followed by one 30-minute readout. Replaces Templates A, B and C for fast projects. Keep it to what decides go or no-go.

### 1. Verdict and conditions to proceed
**Verdict:** [Proceed / Proceed with conditions / Stop]
[Two or three sentences: the most important insight.]
What the design gets right: [one or two strengths, each with the failure it prevents.]
Conditions before go-live, each with its acceptance test:
1. **[ID]:** [condition]. Done when: [test].

### 2. Flows reviewed
| Flow | Touches (keys, money, identity, admin) | Tier |
| --- | --- | --- |

### 3. Findings
Every Critical and High finding, Critical first. Medium and Low findings follow in one grouped line per severity.
| ID | Finding | Severity | Source and evidence | Fix (pattern) | Done when |
| --- | --- | --- | --- | --- | --- |
Evidence: Verified with link, or Unverified. Every Unverified finding's "Done when" test doubles as its verification.

### 4. Assumptions we made
Instead of a question round. Correct any that are wrong at the readout.
| # | We assumed | Affects | If wrong |
| --- | --- | --- | --- |
| A1 | [assumption about an unstated or illegible point] | [finding IDs] | [finding is withdrawn / severity changes to X / new finding] |

### 5. Most likely attack path
[Three lines: start, steps by finding ID, outcome.]

### 6. Not reviewed
[Inputs missing, flows out of scope, nothing verified in code, claims not verified against current sources: one short list.]

### 7. Readout agenda (30 minutes)
1. Correct assumptions (10 minutes)
2. Agree owners and dates for conditions (15 minutes)
3. Risk acceptances, if any (5 minutes)

After the readout, findings are closed when their acceptance tests pass in the team's own test suite. No second review unless the design changes materially.

## Template F: architect self-check

For architects to run on their own design before submitting it. Produces a short list they can fix themselves, so the security review starts from a cleaner design.
1. **Completeness gaps** in the design, from the checklist, each with a one-line suggestion.
2. **Likely findings** the security review would raise, at most five, each with the recommended pattern.
3. **Assumptions to state explicitly** in the design so reviewers do not have to guess.
Tone: helpful and specific; no severity ratings or verdict, since this is not the review itself.
