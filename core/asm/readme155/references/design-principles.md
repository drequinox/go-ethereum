# Custody design principles, with industry comparison

Thirteen vendor-neutral principles for digital asset custody and wallet design. They are the "why" beneath the checks in the lenses, and the source of the one design principle each review names in its recommendations (Pass 9).

Each principle has: the principle; the threat it answers; what the review asks; **how the industry does it**, as comparison only; and what to watch for.

## How to use this file

1. **Principles are the criterion; the industry is a comparison.** Findings and severities come from the principles, the threat model and the evidence, never from what a vendor does. "Vendor X does it" can support a recommendation by showing it is achievable and normal. It is never the reason for a finding. "Nobody in the market does it" is never a reason to downgrade one.
2. **Vendor documentation describes intent, not assurance.** Major providers have shipped serious flaws (see BitForge and TSSHOCK in [incidents.md](incidents.md)). Never write that a design is secure because it matches a vendor.
3. **Cite and date.** Each comparison below is from the vendor's own documentation, checked on 17 October 2026. Re-check any comparison a High or Critical recommendation relies on (external verification rule in SKILL.md). Never put internal names or designs in a search query.
4. **Neutral.** No ranking of vendors. Name a platform only as an example of a pattern.
5. **In a recommendation,** write the principle in the Requirement, and if it helps persuade, add one line: "Industry comparison: [pattern], documented by [platforms, with links]."

---

### DP-1. Policy is enforced where the key is

**Principle.** The decision to sign is made, or verified, inside the boundary that holds the key: the signer, HSM, enclave or MPC node. A policy enforced only by an application in front of the signer is advice, not control.
**Threat.** A compromised application, API server or database sends the signer a request that policy would have refused.
**Review asks.** Where is policy evaluated? Does the signer verify the decision and the approvals itself, or trust a flag from the caller?
**Industry comparison.**
- Anchorage documents custom logic in its HSMs that checks for a valid client quorum and Anchorage approval before signing, so that a compromised server or app cannot bypass the rules ([Anchorage](https://docs.anchorage.com/knowledge-base/platform/users/security)).
- Turnkey runs its policy engine in a secure enclave that returns a signed ruling (allow or deny), which the signer enclave relies on; the database, coordinator and API gateway are treated as untrusted ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Ledger Enterprise describes HSMs that check governance rules before transactions reach the chain ([Ledger Enterprise](https://enterprise.ledger.com/protect/)).
- Fireblocks describes governance rules held in secure enclave storage so that attackers and insiders cannot modify them ([Fireblocks](https://www.fireblocks.com/platforms/governance-and-policy-engine/)).
**Watch for.** Marketing language that does not say where evaluation happens: ask, and get it in writing.

### DP-2. Approvers sign intent, not bytes

**Principle.** What people approve is a structured intent (asset, amount, destination, contract and function). A trusted component builds the transaction from that intent, or fully decodes it and checks that it matches. Anything that cannot be decoded fails closed.
**Threat.** Blind signing and approve-then-edit: an approved request differs from what is signed (Bybit, WazirX).
**Review asks.** What exactly does the approval signature cover? Can raw hashes, arbitrary messages or contract calls reach the signer, and what happens to them?
**Industry comparison.**
- Anchorage describes HSMs that construct the transaction from a quorum of cryptographically signed intents ([Anchorage](https://anchorage.com/insights/how-anchorage-digital-protects-clients)).
- Turnkey runs a parser in an enclave that extracts metadata from unsigned Solana and EVM transactions for use in policies ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Dfns amount and recipient rules evaluate plain value transfers only, and fail closed (trigger) for raw signatures, swaps, contract calls and zero-value transactions ([Dfns](https://docs.dfns.co/core-concepts/policies.md)).
**Watch for.** Policies that silently pass transaction types they cannot parse.

### DP-3. Authenticate the person for each action, not the session

**Principle.** Every state-changing action is signed by the actor's own authenticator (passkey, hardware key, or a workload's private key), over the request contents and a time or nonce, and verified inside the trusted boundary.
**Threat.** A stolen session, compromised gateway or malicious insider forges an approval or a change.
**Review asks.** Is each approval, policy change and user change signed by the person, and verified by the component that acts on it? Is replay prevented?
**Industry comparison.**
- Dfns requires every state-changing API call to be signed by a user (WebAuthn passkey) or service account (private key) through User Action Signing ([Dfns](https://docs.dfns.co/d/api-docs/authentication/user-action-signing)).
- Turnkey requests carry "stamps": signatures by user-held keys over the full request body, with a timestamp checked against the enclave's secure time source to block replay ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Fireblocks' mobile app requires a PIN plus biometrics or a YubiKey for each approval or key access, not only at login ([Fireblocks](https://support.fireblocks.io/hc/en-us/articles/9205187986844-Security-aspects-Signing-with-the-Fireblocks-mobile-app)).
- Anchorage signs API requests with Ed25519 keys scoped by permission group, and requires biometrics on iOS for every approval ([Anchorage](https://docs.anchorage.com/knowledge-base/platform/users/security)).
**Watch for.** Signatures verified only at the gateway, which a compromised service behind it can bypass.

### DP-4. Govern the governors

**Principle.** Changes to policies, quorums, approvers, allow-lists, roles and the code that enforces them need at least as much authority as the actions they control. They do not silently change approvals already in flight.
**Threat.** The governance layer is the easiest route: change the rule, then move the funds.
**Review asks.** Who can change policy, add an approver or edit the allow-list, and with how many people? What happens to pending requests when policy changes?
**Industry comparison.**
- Fireblocks uses an Admin Quorum for sensitive workspace changes such as adding users and whitelisted addresses, approved with a separate configuration key on the device ([Fireblocks](https://developers.fireblocks.com/docs/capabilities), [mobile security](https://support.fireblocks.io/hc/en-us/articles/9205187986844-Security-aspects-Signing-with-the-Fireblocks-mobile-app)).
- Turnkey organisations have a Root Quorum, with a multi-party threshold recommended ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Anchorage supports separate sub-quorums for withdrawals, staking and governance ([Anchorage](https://docs.anchorage.com/knowledge-base/platform/users/security)).
**Watch for.** Dfns documents that approval groups and quorums are evaluated live, so lowering a quorum can clear a pending request immediately ([Dfns](https://docs.dfns.co/core-concepts/policies.md)). Where a platform behaves like this, the policy change itself must sit under a policy.

### DP-5. Independence over count

**Principle.** A threshold counts only independent parties: different people, devices, software, infrastructure and, for the highest value, organisations. Where the firm carries the liability, it holds a share or approval that cannot be bypassed.
**Threat.** Common-mode compromise: several "approvers" on one laptop image, one cloud account, one vendor or one UI (Ronin, Bybit, Radiant).
**Review asks.** What single compromise would satisfy the threshold? Does the firm hold a veto, or only a vendor?
**Industry comparison.**
- Dfns documents t-of-n signers (3 of 5 recommended), with a hybrid model in which the customer runs some signers and so becomes a required participant with "a cryptographic veto over any transaction" ([Dfns](https://docs.dfns.co/advanced/deployment-models/mpc)).
- BitGo wallets use three keys (user, backup, BitGo) with 2-of-3 signing; in custody, no one person controls more than one key for a wallet ([BitGo](https://developers.bitgo.com/guides/get-started/concepts/wallet-types)).
- Fireblocks Key Link lets an organisation keep keys in its own HSM while using the platform's governance ([Fireblocks](https://developers.fireblocks.com/docs/capabilities)).
**Watch for.** Who manages the encryption keys for stored shares: in Dfns' cloud model, Dfns manages them ([Dfns](https://docs.dfns.co/advanced/deployment-models/mpc)).

### DP-6. What approvers see is independent of what requested it

**Principle.** The approval display is produced by a component the requester does not control, preferably on a dedicated device with a trusted screen, showing the decoded intent.
**Threat.** A compromised interface shows a benign transaction while a malicious one is signed (Bybit, WazirX, Radiant).
**Review asks.** Which component renders what the approver sees, and could the same compromise alter both the request and the display?
**Industry comparison.**
- Ledger Enterprise uses personal security devices with clear signing ("what you see is what you sign") for approvals ([Ledger Enterprise](https://enterprise.ledger.com/protect/)).
- Fireblocks designated signers review and confirm transaction details on the mobile app before authenticating ([Fireblocks](https://support.fireblocks.io/hc/en-us/articles/9205187986844-Security-aspects-Signing-with-the-Fireblocks-mobile-app)).
- Anchorage offers smart contract simulation with in-app warnings for its self-custody product ([Anchorage](https://anchorage.com/insights/how-anchorage-digital-protects-clients)).
**Watch for.** "Simulation" shown by the same web app that built the transaction: it shares the compromise.

### DP-7. Deny by default; fail closed

**Principle.** With no policy, an unknown transaction type, a timeout, or a dependency down, the answer is deny. Deny rules take precedence over allow rules.
**Threat.** Gaps in policy coverage become open doors.
**Review asks.** What does a new wallet, an untagged wallet, or an unparseable transaction get by default? What happens on timeout?
**Industry comparison.**
- Turnkey: deny takes precedence over allow ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Dfns: block always wins over request approval, and amount rules fail closed for transaction types they cannot evaluate ([Dfns](https://docs.dfns.co/core-concepts/policies.md)).
- Fireblocks: if a co-signer callback handler does not respond within 30 seconds, the request fails ([Fireblocks](https://developers.fireblocks.com/docs/cosigner-architecture-overview)).
**Watch for.** Allow-all baselines. Dfns policies restrict an allow-all baseline and can be scoped by wallet tags, so untagged wallets are not covered; delegated wallets bypass the policy engine entirely ([Dfns](https://docs.dfns.co/core-concepts/policies.md)).

### DP-8. Machines are governed approvers

**Principle.** Automated signing and approval run in an isolated component, with approval logic the firm writes and controls, scoped and rate-limited, and never defaulting to approve.
**Threat.** An API credential or bot becomes an unlimited, silent approver.
**Review asks.** What can automation sign or approve without a person? What happens if its decision logic is missing or down?
**Industry comparison.**
- Fireblocks API Co-signer runs in an enclave (Intel SGX, AWS Nitro or Google Cloud Confidential Space) and calls a customer callback handler to approve or deny each request ([Fireblocks](https://developers.fireblocks.com/docs/cosigner-architecture-overview)).
- Dfns lets service accounts count toward a quorum only if a group explicitly allows it, which Dfns must enable ([Dfns](https://docs.dfns.co/core-concepts/policies.md)).
**Watch for.** Fireblocks documents that without a callback handler the co-signer automatically signs or approves all requests for that API user ([Fireblocks](https://developers.fireblocks.com/docs/cosigner-architecture-overview)). Check that the handler exists and fails closed.

### DP-9. An independent second check, scaled to value

**Principle.** High-value or unusual actions get a check by a party or system independent of the requester's organisation: anomaly detection, human confirmation, a time delay, or a second operator.
**Threat.** A whole client quorum is socially engineered or compromised together.
**Review asks.** What independent check exists beyond the client's own approvers, and does it scale with value and unusualness?
**Industry comparison.**
- Anchorage reviews every custodial transaction itself, combining human confirmation with automated outlier detection over biometrics, transaction details and location ([Anchorage](https://docs.anchorage.com/knowledge-base/platform/users/security)).
- BitGo custody withdrawals require video ID verification with a BitGo operator, and a second operator signs with the BitGo key ([BitGo](https://developers.bitgo.com/guides/get-started/concepts/wallet-types)).
**Watch for.** Second checks that can be waived by the same people they are meant to check.

### DP-10. Tiers are defined by where the last share lives and how approval reaches it

**Principle.** Hot, warm and cold are defined by where the final key or share sits and how approval travels to it, not by labels. Crossing tiers needs stronger approval than moving within one.
**Threat.** "Cold" wallets that can be signed remotely in minutes.
**Review asks.** For each tier, where is the final share, how does approval reach it, and how long does it take?
**Industry comparison.**
- Fireblocks defines hot as the third share on an API co-signer, warm as on an internet-connected mobile device, and cold as on an air-gapped device approved by QR codes; a workspace cannot be both cold and hot or warm ([Fireblocks](https://developers.fireblocks.com/docs/capabilities)).
- BitGo custody wallets are all cold, with a 24-hour withdrawal service level ([BitGo](https://developers.bitgo.com/guides/get-started/concepts/wallet-types)).

### DP-11. Recoverable without the vendor, but never by one person

**Principle.** Backups exist before value is at risk, are separated from their decryption keys under independent custody, and recovery is rehearsed, including without the vendor.
**Threat.** Lockout after vendor failure, or a backup that becomes the weakest copy of the key.
**Review asks.** Can the firm recover if the vendor disappears? How many people does it take?
**Industry comparison.**
- Fireblocks requires key-share backups by default for embedded wallets, encrypted with a key held separately from the stored backup ([Fireblocks](https://developers.fireblocks.com/docs/backup-and-recovery-overview)).
- BitGo self-custody wallets leave the user and backup keys with the customer ([BitGo](https://developers.bitgo.com/guides/get-started/concepts/wallet-types)).
- Dfns offers disaster-recovery backups to the customer's own storage for self-hosted signers ([Dfns](https://docs.dfns.co/advanced/deployment-models/mpc)).
**Watch for.** Backups that a single person can decrypt; recovery that has never been tested end to end.

### DP-12. Minimise and verify what you trust

**Principle.** Name the components that are trusted; everything else, including databases, gateways and coordinators, cannot affect keys or policy. The code that enforces policy is attested, and deploying it is quorum-governed.
**Threat.** A broad trusted base, or a single engineer who can deploy the policy engine.
**Review asks.** What is in the trusted base? Can anyone verify the code that runs there? Who can change it?
**Industry comparison.**
- Turnkey treats only its enclave applications as trusted, and uses remote attestation and boot proofs to tie enclave binaries to source code ([Turnkey](https://whitepaper.turnkey.com/architecture)).
- Anchorage notes that its server and app never hold plaintext key material, so compromising them cannot bypass the HSM's rules ([Anchorage](https://docs.anchorage.com/knowledge-base/platform/users/security)).
**Watch for.** Attestation that is internal only. Turnkey documents that boot proofs are currently used internally, with external app proofs planned ([Turnkey](https://whitepaper.turnkey.com/architecture)).

### DP-13. Reduce exposure you do not control

**Principle.** Limit assets held at counterparties, exchanges and bridges, and prefer settlement arrangements that keep assets under your custody.
**Threat.** Exchange insolvency or bridge failure, which is binary and often total.
**Review asks.** What value sits outside the firm's custody, with whom, for how long?
**Industry comparison.**
- Copper ClearLoop keeps delegated funds locked in an omnibus account while the exchange shows a matching virtual balance, settling every 2, 4 or 24 hours depending on the exchange; Copper says it mitigates counterparty and insolvency risk ([Copper](https://developer.copper.co/guides/clearloop/introduction.md)).
**Watch for.** Exposure between settlement cycles, and the settlement provider becoming the new concentration.

---

## Questions for any wallet or custody vendor

Use these to build the shared-responsibility table in [custody.md](custody.md). Ask for documentation, not answers in a meeting.

1. Where exactly is policy evaluated, and does the signer verify the decision and the approvals itself? (DP-1)
2. What does an approval signature cover, and what happens to transaction types the policy cannot parse? (DP-2, DP-7)
3. Which actions must be signed by the user's own authenticator, and where is that signature verified? (DP-3)
4. Who can change policies, quorums, approvers and allow-lists, and what happens to pending approvals when they change? (DP-4)
5. What is the default for a new or untagged wallet, and do any wallet types bypass policy? (DP-7)
6. Where are key shares held, who manages their encryption keys, and can the firm hold a required share? (DP-5)
7. What do approvers see, rendered by which component, on which device? (DP-6)
8. What happens if automated approval logic is missing, slow or down? (DP-8)
9. Which MPC protocol and implementation version, with what evidence that the 2023 BitForge and TSSHOCK class fixes are in? ([cryptography.md](cryptography.md))
10. Can the firm recover funds without the vendor, and has that been tested? (DP-11)
11. What runs in the trusted base, how is it attested, and who can deploy to it? (DP-12)
12. What independent audits, certifications and penetration tests cover the parts the firm relies on, and how are incidents notified?

## Sources

All checked 17 October 2026: [Anchorage security](https://docs.anchorage.com/knowledge-base/platform/users/security), [Anchorage client protection](https://anchorage.com/insights/how-anchorage-digital-protects-clients), [BitGo wallet types](https://developers.bitgo.com/guides/get-started/concepts/wallet-types), [Copper ClearLoop](https://developer.copper.co/guides/clearloop/introduction.md), [Dfns policies](https://docs.dfns.co/core-concepts/policies.md), [Dfns User Action Signing](https://docs.dfns.co/d/api-docs/authentication/user-action-signing), [Dfns MPC deployment models](https://docs.dfns.co/advanced/deployment-models/mpc), [Fireblocks capabilities](https://developers.fireblocks.com/docs/capabilities), [Fireblocks API Co-signer](https://developers.fireblocks.com/docs/cosigner-architecture-overview), [Fireblocks mobile signing](https://support.fireblocks.io/hc/en-us/articles/9205187986844-Security-aspects-Signing-with-the-Fireblocks-mobile-app), [Fireblocks policy engine](https://www.fireblocks.com/platforms/governance-and-policy-engine/), [Fireblocks backup and recovery](https://developers.fireblocks.com/docs/backup-and-recovery-overview), [Ledger Enterprise](https://enterprise.ledger.com/protect/), [Turnkey architecture](https://whitepaper.turnkey.com/architecture).
