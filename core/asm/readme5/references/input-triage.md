# Input triage and the system model

Any input is acceptable. The goal of triage is one normalised system model that every later pass works from, plus an honest list of what the inputs do not say.

## Per input type

| Input | Extract | Watch for |
| --- | --- | --- |
| Diagram image (PNG, JPG, screenshot) | Lifelines or components, every arrow with its label, step numbers, notes, states and transitions, legend | Small or blurred labels: list each as illegible and ask. Do not guess. Marks whose meaning is not explained (ticks, colours): ask. |
| Diagram source (Mermaid, PlantUML, draw.io or Visio XML) | Same as images, read from source text | Elements present in source but hidden in the rendered view |
| HTML design pages | Two tools, run first if you can run commands (otherwise ask the user to). `scripts/html_to_review.py` turns each page into clean text: headings, tables, code, expanded `<details>`, SVG labels, Mermaid source, embedded images saved as files; it marks diagram regions drawn in HTML/CSS. `scripts/extract_diagrams.py` renders the page in a browser and reconstructs every diagram (HTML/CSS or SVG) as boxes and connections, "from -> to : label", with step numbers and direction, plus a screenshot of each. Without Playwright, the user can paste `scripts/diagram_extract.js` into the browser Console and run `extractAllDiagrams()`. Use the `.diagrams.md` connections as the flow, the `.review.md` text for context, and the screenshots to confirm. | Anything listed as unresolved or "direction unknown" must be checked against the screenshot, never guessed. Canvas-drawn diagrams have no elements to read: use the screenshot. Collapsed sections often hold the step-by-step detail. |
| Architecture document or design note | Components, responsibilities, stated controls, assumptions, non-functional requirements, open issues | Words like "always", "never", "atomic", "secure", "encrypted" without a mechanism: these are claims to verify |
| API specification (OpenAPI, gRPC, GraphQL) | Every state-changing operation, its authentication scheme, required permissions, request fields that change behaviour, idempotency, error codes | Optional fields that change ownership, scope or destination; endpoints that mutate after approval |
| Vendor documentation | What the vendor enforces, what the integrator must configure, defaults, irreversible operations, limits | Defaults that are permissive; features documented in one page but contradicted in another. Cite every vendor claim. |
| Code | Enforcement points: authentication, authorisation, policy checks, cryptographic calls, key handling, state transitions, retries, logging | Checks in the UI or caller but not the service; fail-open error handling; secrets in code |
| Infrastructure as code, configuration | Identities and their permissions, network paths, secret mounts, key management settings, logging destinations | Shared credentials, wildcard permissions, public endpoints, missing encryption or logging |
| Runbooks, ceremony scripts | Who does what, with which device, under which approvals | Single-person steps, unverifiable steps, steps done on general-purpose machines |
| Meeting notes, emails, tickets | Decisions, known issues, deadlines | Decisions that contradict the documented design |
| Prior reviews and incident reports | Open findings, accepted risks, lessons | Accepted risks whose conditions have since changed |

## The system model

Build this before analysing anything. Keep it in working memory; include a condensed version in the output.

1. **Assets**, each with value at risk if known: private keys and shares, client funds, signing authority, approval authority, credentials, personal and client data, audit records, configuration that grants rights.
2. **Actors**: people and roles (client admin, client approver, staff operator, platform admin, auditor), services, vendors, external parties.
3. **Components and data stores**, with owner and hosting.
4. **Numbered data flows**: who calls whom, with what, authenticated how, carrying which asset.
5. **Trust boundaries**: client to platform, internet to internal, service to service, application to signer, firm to vendor, hot to cold environments, human to machine.
6. **Lifecycle states** of the main objects and the transitions between them, with who may trigger each.
7. **Async paths**: events, queues, webhooks, batch jobs, retries, and what state the system is in while they are pending.
8. **External dependencies**: vendors, nodes, oracles, identity providers, KYC and KYT providers.
9. **Claimed controls**: every control the inputs assert, marked Claimed until verified.
10. **Contradictions and gaps**: where inputs disagree, and what is missing or illegible.

## When inputs are thin

- With only a diagram, the review is a design review: most findings will be Unverified, and the questions list matters more than the findings list.
- With only vendor documentation, take the integrator's perspective: the shared-responsibility table becomes the spine of the review.
- With code but no design, reconstruct the flow from the code, then review it as if it were the design, and flag every place where intent cannot be inferred.
