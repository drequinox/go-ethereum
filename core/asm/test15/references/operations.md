# Operations and resilience lens

Prevention fails eventually. This lens asks whether an attack would be noticed, how fast it could be stopped, and whether people, devices, vendors and the build pipeline are part of the threat model.

## Detect

| Check | Why it matters |
| --- | --- |
| Alerts on: signing outside the approved path, new destinations, policy or quorum changes, approver additions, failed or aborted signing sessions, unusual volume or timing | These are the early signals of every major custody incident |
| Alerts reach a staffed function 24/7 with a defined response time | Crypto markets and attackers do not keep office hours |
| Logs of approvals, signing and configuration changes go to a store the operators of the system cannot alter | Attackers clean up after themselves |
| On-chain monitoring of the firm's own addresses, independent of the internal ledger | Catches movements the internal system did not record |

## Respond

| Check | Why it matters |
| --- | --- |
| A kill switch or freeze that halts signing or withdrawals quickly, usable by one authorised person, with restoration requiring a quorum | Fast containment with slow, controlled recovery |
| Runbooks for key compromise, approver compromise, vendor compromise and signer outage, rehearsed | Untested runbooks fail under pressure |
| Pre-agreed contacts with chain analytics firms, exchanges and law enforcement for freezing stolen funds | Recovery odds fall sharply within hours |

## People and devices

| Check | Why it matters |
| --- | --- |
| Approvers and operators are trained on social engineering, fake recruiter approaches and fake vendor contacts | State-sponsored groups have repeatedly entered through staff and contractors |
| Signing and approval happen on dedicated, hardened devices with restricted software | Malware on general-purpose devices has defeated multisig controls |
| Joiner, mover and leaver processes revoke access, credentials and quorum membership promptly | Stale approvers are standing risk |
| Two-person integrity for privileged operational actions, including production access | Single administrators can bypass application controls entirely |

## Supply chain and vendors

| Check | Why it matters |
| --- | --- |
| Front-end code served to approvers is integrity-protected (pinned versions, subresource integrity, or locally built and verified) | Compromised UI bundles have been used to make approvers sign malicious transactions |
| Dependencies are pinned, scanned and reviewed; build pipelines are hardened with provenance (for example SLSA-style attestations) | Package compromises have drained wallets through trusted libraries |
| Each vendor in the custody path has a documented trust model, access scope and exit plan | Vendor compromise or failure must be survivable |
| Vendor access to production is time-bound, approved and logged | Standing vendor access is an unmonitored path |

## Continuity

| Check | Why it matters |
| --- | --- |
| Recovery time and recovery point objectives for signing are defined and tested | Unavailability of signing is itself a business and regulatory risk |
| Loss of a key person, location, cloud region or vendor has a rehearsed plan | Custody must survive any single loss |
