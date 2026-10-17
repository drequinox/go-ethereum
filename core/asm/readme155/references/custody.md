# Custody and key lifecycle lens

Apply to wallets, vaults, signing services, approval quorums, policy engines, withdrawal flows, client onboarding to custody, and backup and recovery.

## Wallet tiers and value at risk

| Check | Why it matters |
| --- | --- |
| Hot, warm and cold tiers are defined, with limits on value held in each and an automated rebalancing rule | Value at risk in online systems should be bounded by design |
| Movement from cold to warm to hot needs stronger approval than movement within a tier | Tier boundaries are only meaningful if crossing them is harder |
| Client assets are segregated (per-client wallets or a ledger that reconciles omnibus holdings to clients) | Commingling complicates recovery, insolvency treatment and regulatory reporting |

## Signing architecture

| Check | Why it matters |
| --- | --- |
| The policy decision is enforced by the signer (or a co-signer the application cannot bypass), not only by the application in front of it | If the application is compromised, an application-only policy is no policy |
| The signer verifies approvals itself: distinct approvers, valid signatures, bound to the exact payload, not expired | Otherwise approvals are just flags in a database |
| What the signer signs is constructed or independently decoded by a trusted component, not taken as opaque bytes from the caller | Opaque payloads are blind signing |
| Raw-message and arbitrary-contract signing are disabled by default and governed when enabled | They bypass destination and amount controls |
| Signing capacity, latency and failure behaviour are known (HSM or MPC throughput under peak) | A signer outage freezes withdrawals and can force unsafe workarounds |

## Quorum design

| Check | Why it matters |
| --- | --- |
| Threshold is meaningful: compromise of any threshold-minus-one parties cannot sign | Low thresholds (for example 2 of 5) have been the root of large bridge losses |
| Quorum members are independent: different reporting lines, devices, networks and, where possible, locations and vendors | Common-mode compromise (same laptop image, same UI, same vendor) defeats the threshold |
| Approvers use dedicated signing devices or hardened workstations, not general-purpose machines | Malware on approver machines has defeated multisig in practice |
| The initiator cannot approve their own request | Otherwise the quorum is one person short |
| Changes to quorum membership, thresholds and policies need a quorum at least as strong as the actions they govern | Otherwise the governance layer is the easiest attack path |
| Restoring capability (unfreezing, unblocking, re-adding an approver) is as controlled as removing it | Attackers target the restore path |
| The people who can deploy code or configuration to the signer, policy engine, approval UI or address book are counted as part of the control set, and their deployments need two-person approval | A malicious deployment bypasses every quorum; the Bybit loss came through code served to signers |

## Approver experience and blind signing

| Check | Why it matters |
| --- | --- |
| Approvers see a human-readable decoding of exactly what will be signed: destination, amount, asset, chain, contract call and its effect | Most large custody losses since 2024 involved approvers signing something other than what they saw |
| The decoding is produced on a separate path from the one that built the transaction (independent verification) | A compromised UI can display one thing and submit another |
| Dangerous operations (delegatecall, ownership or implementation changes, unlimited approvals, permit signatures) are flagged and need an extra approval or a time delay | These turn one signature into total loss |
| Transactions are simulated before signing and the predicted state changes are shown to approvers | Simulation catches effects the decoding misses |

## Withdrawal and destination controls

| Check | Why it matters |
| --- | --- |
| Destinations are allow-listed, and changes to the allow-list are dual-controlled with a cooling-off period before first use | Most theft needs a new destination |
| Large or unusual withdrawals carry a time delay that a separate party can cancel | Gives detection time to act before irreversible loss |
| Velocity limits per wallet, per client and per time window | Bounds the loss from a single compromise |
| Address integrity: addresses are compared in full, look-alike and recently seen poisoning addresses are flagged | Address poisoning relies on truncated display |
| Sanctions and KYT screening happen before signing and fail closed | Regulatory breach is itself a High impact |

## Key ceremonies and lifecycle

| Check | Why it matters |
| --- | --- |
| Generation, backup, rotation and destruction follow written ceremony scripts with named roles, witnesses and recorded evidence | Undocumented ceremonies cannot be audited or repeated |
| Ceremonies use air-gapped or dedicated equipment with tamper-evident handling | General-purpose equipment is an extraction path |
| Each key has an owner, purpose, lifecycle state and planned rotation or retirement | Orphaned keys are unmonitored keys |
| Key destruction is verifiable and recorded | Retired keys that still exist still carry risk |

## Backup, recovery and continuity

| Check | Why it matters |
| --- | --- |
| Every key or key share has a backup before it can receive value | A new wallet without backup is a single point of loss |
| Backups are split across independent custodians and locations; no single custodian can restore | Backups must not be the easy path to the key |
| Recovery is rehearsed end to end on a schedule, with measured time to restore signing | Recovery that has not been rehearsed will not meet its target |
| Disaster recovery covers loss of the signing vendor, the cloud region and key personnel | Custody must survive the loss of any one dependency |
| Recovery procedures cannot be triggered by one person or by a support ticket | Recovery flows are a favourite social-engineering target |

## Reconciliation and proof

| Check | Why it matters |
| --- | --- |
| On-chain balances reconcile to the internal ledger on a defined schedule, with breaks escalated | Unreconciled differences hide theft and bugs |
| Every on-chain movement maps to an approved request; unmatched movements raise an alert | Detects signing outside the approved path |
| Every key the signer holds maps to a known wallet and owner; unmatched keys are investigated | Detects orphans and shadow keys |

## Vendor custody (MPC or wallet-as-a-service)

Build a shared-responsibility table: for each control above, mark Vendor enforces, Integrator configures, Integrator enforces, or Not covered. Cite the vendor's documentation for every Vendor entry. Typical integrator-owned gaps: permissive defaults, policy scope, who can create or delegate keys, approver device security, and monitoring. Ask the vendor the questions in [design-principles.md](design-principles.md), and get the answers from documentation.
