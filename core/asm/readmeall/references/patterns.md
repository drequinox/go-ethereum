# Recommendation patterns

Cite by ID in recommendations ("Apply P-02 to the approval step"). Each pattern has a meaning and an acceptance test, so the architects know what done looks like. Add new patterns when a review produces a fix that will recur.

| ID | Pattern | What it means | Acceptance test |
| --- | --- | --- | --- |
| P-01 | Dual control via quorum | High-impact actions need two distinct approvers; the initiator cannot approve | One person's request stays pending; self-approval refused |
| P-02 | Approve the content, not the ID | Approvers sign a hash of the canonical parameters; execution recomputes and verifies it | Editing parameters after approval is refused |
| P-03 | Pending until confirmed | An object stays unusable until every dependent control (policy, backup, provisioning) confirms | With the dependency stopped, the object cannot be used |
| P-04 | Deny by default | A missing policy, entitlement or quota means deny | An object with nothing configured is refused |
| P-05 | Fail-closed status check | Privileged actions check current status; unknown status means refuse | A blocked entity is refused in every service within one minute |
| P-06 | Easy to stop, hard to restart | One person can suspend; restoring capability needs the quorum | Unblock by one person stays pending |
| P-07 | Verified bootstrap | First admin or signer: verified identity, single-use short-lived invite, phishing-resistant credential before any privilege | Reused or expired invite fails; no privilege before enrolment |
| P-08 | One credential per caller, least privilege | Each workload has its own scoped, short-lived credential | Each credential is held by one workload; out-of-role calls refused |
| P-09 | Idempotent by request ID, with reconciliation | Retries reuse the same request ID; a job reconciles systems of record | Fault injection yields exactly one object |
| P-10 | Append-only, independent audit | Insert-only grants, hash chain, write-once copy outside the system operators' control | Updates denied; tampering detected |
| P-11 | Independently verify what is displayed | A separate component re-derives addresses or decodes payloads before display | A swapped value is detected before the user acts |
| P-12 | Govern the scope, not just the rule | Changes to tags, filters or group membership that decide coverage need approval; baselines without filters cover new objects | Removing scope needs approval; a new untagged object is still covered |
| P-13 | Signer-enforced policy | The signer or a co-signer the application cannot bypass evaluates policy and verifies approvals | With the application compromised in a test, an unapproved payload is not signed |
| P-14 | Independent quorum | Quorum members differ in device, software path, reporting line and, where possible, vendor and location | No single device image, interface or vendor compromise can produce a quorum |
| P-15 | Time delay with cancel | Large, unusual or new-destination transfers and all upgrades wait a defined period, cancellable by a separate party | A flagged transfer can be cancelled during the delay; it cannot be expedited by one person |
| P-16 | Governed allow-list with cooling-off | Destinations and contract interactions are allow-listed; additions are dual-controlled and usable only after a cooling-off period | A new destination added today cannot receive funds until the period ends |
| P-17 | Typed signing only | The signer accepts structured, decodable payloads; raw-hash and arbitrary-message signing are disabled or separately governed | A raw-hash signing request is refused |
| P-18 | Dangerous-call guard | delegatecall, ownership, module, guard and implementation changes, unlimited approvals and permit signatures are blocked or need elevated approval and delay | Such a transaction is held for elevated approval in a test |
| P-19 | Kill switch | One authorised person can halt signing or withdrawals within minutes; restart needs a quorum | Freeze takes effect within the target time; restart by one person is refused |
| P-20 | Ledger to chain reconciliation | Every on-chain movement maps to an approved request and every signer key to a known wallet; breaks alert | An injected unmatched movement raises an alert within the target time |
| P-21 | Hardened derivation and xpub protection | Account-level hardened derivation; extended public keys treated as sensitive; paths assigned by the system | Callers cannot choose paths; xpubs are not exposed outside the custody boundary |
| P-22 | Rehearsed recovery | Backup before value, split custody of backup keys, scheduled end-to-end restore drills with measured time | Last drill restored signing within the target time |
