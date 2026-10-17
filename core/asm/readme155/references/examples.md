# Calibration examples

## A good finding

> **TO-05, High (Medium × High), design flaw.** Blocking an organisation needs a staff quorum, but unblock and reactivate carry no quorum in the state diagram (transitions BLOCKED to OPERATING, SUSPENDED to OPERATING). Source: supplied state diagram. Unverified. A single staff member, or one compromised staff account, could restore a blocked organisation. Fix: the same quorum to restore as to remove, verified against approval records (P-06, P-01). Test: an unblock by one person stays pending.

Why it works: specific transition, source, evidence status, attacker consequence, rubric-consistent rating, pattern, test.

## A bad finding (never write these)

> The system should follow security best practices such as MFA, least privilege and encryption at rest.

Why it fails: no step, no mechanism, no evidence, no consequence, no test, and it may already be covered.

## A good cryptography finding

> **KD-02, High (Medium × High), design flaw.** Wallet addresses are derived with non-hardened BIP32 paths below the account level (design doc section 4.2), and the account xpub is shared with the reporting service (architecture diagram, arrow 7). If any child private key leaks, the xpub allows recovery of the account private key and every sibling key. Unverified. Fix: hardened derivation at the account level and treat xpubs as sensitive (P-21). Test: the reporting service holds only addresses, not xpubs.

## A good recommendation, with principle and industry comparison

> **R1. Enforce withdrawal policy at the signer (CW-02, CW-01; P-01).** Design principle: DP-1, policy is enforced where the key is.
> - **Requirement:** the HSM signs a withdrawal only after itself verifying a quorum of approver signatures over the exact asset, amount and destination.
> - **Recommended design:** approvers sign a structured intent with their passkeys; the signing service passes the signed intents to the HSM, whose custom logic verifies them and builds the transaction (DP-2).
> - **Alternatives:** a co-signer in an enclave that the application cannot bypass, holding a required share.
> - **Effort:** medium; the HSM supports custom logic.
> - **Accepted when:** a withdrawal whose destination is edited after approval is refused by the HSM, with the application fully compromised in the test.
> - **Industry comparison:** Anchorage documents HSM logic that checks client quorum before signing, and Turnkey a policy enclave whose signed ruling the signer relies on ([links in design-principles.md]).

Why it works: the principle carries the argument; the requirement and test stand on their own; the comparison shows it is achievable and normal, without making a vendor the standard.

Never write: "Fireblocks does not do this, so it is acceptable" or "this matches Dfns, so it is secure".

## A good attack path

> **AP-1: move client funds to an attacker address.** Starting position: malware on one approver's laptop. Steps: CW-02 (approval binds request ID, not parameters) lets the attacker edit the destination after approval; CW-01 (new wallets have no policy for a window) removes limits; no time delay applies. Stopped today by: nothing after approval. Detected by: nightly reconciliation only. Outcome: full balance of the targeted wallet, irreversible. Severity: Critical.

Why it works: realistic start, named findings in order, honest about missing detection, irreversibility drives the rating.

## A good architecture risk

> **TO-06, Medium (Medium × Medium), architecture risk.** Schema provisioning runs after the organisation commits (step 6), but no failure state exists between ORG_CREATED and SCHEMA_READY. A failed or partial provisioning leaves an organisation that APIs may treat as usable. Unverified. Fix: a PROVISION_FAILED state with retry and alerting; APIs refuse organisations not yet SCHEMA_READY (P-03). Test: a forced provisioning failure leaves the organisation unusable and raises an alert.

## A good dropped item

> Dropped: "tenant creation is not audited". The tenant row and its event are written in one transaction (step 3). Converted to a question: is the actor's identity recorded with the event?

## A good limitation statement

> The step 11 note and the meaning of the green ticks in the sequence diagram were not legible. Both are listed as questions; no finding depends on them.
