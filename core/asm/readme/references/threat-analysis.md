# Threat analysis method

## Completeness checklist (pass 2)

| Item | What a gap here usually hides |
| --- | --- |
| Actors and steps | Unnamed callers acting with implicit trust |
| Lifecycle states | Objects usable in states nobody designed for |
| Asynchronous steps | A window where the state is unsafe |
| Trust boundaries | Service-to-service calls treated as trusted |
| Authentication on each arrow | Steps any internal caller can trigger |
| Failure, timeout and retry paths | Duplicates, orphans, half-provisioned objects |
| Where data is written, and who can change it | Editable records, including audit |
| Admin, ops and break-glass paths | Backdoors and single-person overrides |
| Isolation model | Cross-tenant or cross-client access |
| Approval before activation | Single-person creation of high-value objects |
| Root of trust (first admin, first key, first approver) | An undefined bootstrap that everything else inherits |
| Credentials and secrets | Shared credentials with too many rights |
| Detection and response | Attacks that succeed silently and cannot be stopped |
| Offboarding and decommissioning | Access and keys that outlive their purpose |

Mark each Yes, Partly or Missing.

## Attacker goals (pass 3)

Start from these and add system-specific ones:

1. Move client or firm assets to an attacker-controlled destination.
2. Obtain a valid signature or approval without legitimate authority.
3. Extract or reconstruct a private key or enough key shares.
4. Deny the firm the ability to sign or recover (lockout, ransom, destroyed backups).
5. Access or alter another tenant's data or assets.
6. Hide or alter evidence of actions taken.
7. Cause a regulatory breach (sanctioned counterparty, missing travel-rule data, unapproved client).

## Invariant lenses (pass 3)

| Lens | Typical invariant |
| --- | --- |
| Secrets | Key material never leaves the signer boundary in usable form |
| Authorisation | Only role R can do A; maker is never checker |
| Binding | What was approved is exactly what is signed and executed |
| State | An object is usable only in state S; states move only along designed transitions |
| Isolation | No cross-tenant read or action |
| Recoverability | A tested backup exists before value is at risk |
| Accountability | Every action is attributable to a person or workload and tamper-evident |
| Consistency | One request produces one object; ledger and chain agree |
| Independence | No single person, device, vendor or code path can satisfy a quorum alone |

Write each as "never X, even if Y". The "even if Y" names the failure the invariant must survive, which is where the tests come from.

## Threat actors (pass 4)

| Actor | Typical capability |
| --- | --- |
| External attacker | Internet access, phishing, credential stuffing, exploitation of exposed services |
| State-sponsored group | Long campaigns, social engineering of staff and vendors, supply-chain compromise, malware on signer devices |
| Malicious or coerced insider | Legitimate access to one role; knowledge of procedures |
| Colluding insiders | Two or more legitimate roles acting together |
| Compromised client admin or end user | The client's own credentials or devices |
| Compromised internal service or workload credential | Any call that service can make |
| Compromised vendor, library or build pipeline | Code or UI served to your users or signers |
| Well-meaning operator | Mistakes under time pressure |

## STRIDE prompts per boundary crossing

| Threat | Ask |
| --- | --- |
| Spoofing | Who is the caller, how is that proven, can the proof be phished, replayed or forged? |
| Tampering | Can the request, payload, parameters or stored state change between check and use? |
| Repudiation | Is the action attributable, signed, and recorded where the actor cannot alter it? |
| Information disclosure | What leaks in transit, at rest, in logs, in errors, to vendors? |
| Denial of service | Can this step be stalled, flooded or forced into an unsafe fallback? |
| Elevation of privilege | Can the caller do more than intended, act for another tenant, or skip a step? |

## Attack trees (pass 4)

For each of the top two or three attacker goals, write a short tree: the goal at the root, two to four alternative routes beneath it, and for each route the conditions that must hold. Mark which conditions the design already prevents. Routes with no preventing condition are where findings come from.

## Hunting techniques (pass 4)

| Technique | Question |
| --- | --- |
| Design vs implementation diff | Where do the diagram, documents, code and walkthrough disagree? |
| The gap question | What can happen between step A and step B, especially around async steps? |
| Approve-then-edit | Is what was approved exactly what executes? |
| Blast radius | Who else holds this credential, and what else can it do? |
| Kill it mid-flow | What is left if this call times out, the process dies or the message is replayed? |
| Who controls the evidence? | Can the actor being audited change the audit? |
| Trust the display? | Could a compromised component show a user something false before they approve? |
| Common-mode failure | Do all approvers, signers or backups share a device type, network, vendor, library or building? |
| Default and fallback | What happens when a policy, configuration or dependency is missing: allow or deny? |
| Restore vs remove | Is restoring a capability as well controlled as removing it? |

## Attack paths (pass 7)

Each path is a short narrative:

> **AP-1: [goal].** Starting position: [actor and access]. Steps: [finding IDs in order, one line each]. Stopped today by: [control, or nothing]. Detected by: [signal, or nothing]. Outcome: [asset and value at risk]. Severity: [rating].

Three paths at most. Prefer the paths that a real adversary, as described in the incident lessons, would actually take.
