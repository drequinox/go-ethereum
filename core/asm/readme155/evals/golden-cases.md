# Golden cases for the security-architecture-review skill

Use these to measure whether the skill finds the right issues, before trusting it on live reviews and whenever you change the skill, the model, or the tool (Claude, VS Code Copilot, Copilot CLI).

## How to run

1. Start a fresh chat for each case, so earlier context cannot leak in.
2. Paste only the **Input** for the case, with: "Run the security-architecture-review skill. Produce Template C."
3. Score the output against **Expected findings** using the scoring rules below.
4. Run each case three times. Consistency across runs matters as much as the score.
5. Record results in the table at the end. Re-run after any edit to SKILL.md.

## Scoring

| Measure | How to score | Target |
| --- | --- | --- |
| Recall | Expected findings matched (same root issue, any wording) / total expected | 80% or more of Highs; 60% or more overall |
| Precision | Findings a reviewer agrees are real / total findings produced | 80% or more |
| Severity agreement | Matched findings rated within one level of expected | 90% or more |
| Evidence discipline | Findings with a source pointer, and Unverified where no evidence was given | 100% |
| Fabrication | Any invented vendor behaviour or invented diagram content | Zero; any instance fails the run |
| Consistency | Highs found in all three runs / Highs found in any run | 80% or more |

A finding that is real but not in the expected list counts toward precision, not against it. Add it to the expected list if it survives review.

---

## Case 1: Create Wallet (in-house, as built)

**Input**

Create Wallet flow, as narrated by the tech lead:
1. User signs in with WebAuthn, picks a vault and chain; client calls POST /v1/wallets.
2. Gateway validates the JWT; wallet service takes org ID from the token and checks the vault belongs to that org.
3. Wallet service stores a pending request; policy engine applies the org's rule (2 of N approvers).
4. Approvers approve with a WebAuthn-signed approval. At quorum, the policy engine publishes an "approved" event carrying the request ID.
5. Wallet service consumes the event, reloads request parameters from Postgres, and calls the HSM over PKCS#11 using the partition password from the secret store. The same secret is mounted in the withdrawal service and an ops admin tool. The partition has one role with generate, sign and unwrap rights.
6. HSM generates a non-extractable secp256k1 key; wallet service derives the address and returns it to the client.
7. Wallet service writes the wallet row with status ACTIVE, then publishes "bind-policy"; the policy engine attaches the policy when it consumes the event. When no policy is found, the engine returns allow.
8. A nightly job at 02:00 UTC wraps new keys to a backup HSM under a 3-of-5 key-encryption key.
9. An audit row is written to the audit_log table in the application database. On HSM timeout the client retries.
A PATCH /v1/wallet-requests/{id} endpoint lets the requester edit a request until it is executed.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | Wallet is ACTIVE before policy is attached; engine allows when no policy exists | High |
| E2 | Approvals bind the request ID, not the parameters; parameters editable after approval | High |
| E3 | One HSM credential shared by three services, with signing rights | High |
| E4 | Address derived and shown by one component without independent check | Medium |
| E5 | HSM call retried without idempotency key; orphan keys | Medium |
| E6 | Audit table editable by the application role | Medium (accept Low to High if reasoned) |
| E7 | Funds can arrive before the nightly backup | Medium |

Must not appear as a finding: "keys can be exported from the HSM" (the key is non-extractable).

---

## Case 2: Tenant and organisation onboarding (architect-supplied)

**Input**

Sequence: (1) Platform admin signs in via firm IdP; token carries platform_admin role. (2) Platform admin creates tenant (name, region group). (3) Tenant ACTIVE and tenant.onboarded written in one transaction. (4) Platform admin creates top-level organisation; sub-organisations may be created by an org admin. (5) Organisation committed with org.onboarded. (6) After commit, tenancy provisions a schema for the organisation (idempotent). (7) Schema and per-schema roles ready; sub-organisations reuse the ancestor schema. (8) Org admin creates business units within its own organisation. (9) Org admin or platform admin opens accounts; account name unique. (10) Platform admin sets counterparty allow-list. (11) Staff set configuration, entitlements, quotas. (12) Org events recorded in outbox, not yet distributed to other services.
States: REQUESTED to TENANT_ACTIVE (platform admin); REQUESTED to REFUSED (wrong role); TENANT_ACTIVE to ORG_CREATED; ORG_CREATED to SCHEMA_READY (after commit); SCHEMA_READY to OPERATING (business units, accounts). OPERATING to SUSPENDED (suspend) and back (reactivate); OPERATING to BLOCKED (block + quorum); BLOCKED to OPERATING (unblock); SUSPENDED, BLOCKED or OPERATING to DEACTIVATED (final). Blocking carries a staff quorum reference.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | No due-diligence or approval gate before activation | High |
| E2 | First org admin bootstrap undefined | High |
| E3 | Single platform admin controls creation, allow-list, entitlements | High |
| E4 | Lifecycle events not distributed; blocked org may act in other services | High |
| E5 | Unblock and reactivate lack quorum; quorum may be a reference only | High |
| E6 | No failure path between ORG_CREATED and SCHEMA_READY | Medium |
| E7 | Sub-organisations share ancestor schema; isolation depends on app code | Medium |
| E8 | Organisation operating before entitlements and quotas set | Medium |
| E9 | Deactivation offboarding undefined | Medium |

Must not appear as a finding: "events can be lost between row write and event" (they are written in one transaction).

---

## Case 3: Vendor integration (Dfns Create Wallet)

**Input**

Provide the Dfns Create Wallet API page and, if the tool can browse, allow it to read the linked Dfns docs on user action signing, policies, idempotency and delegate key. Ask for the integrator's perspective.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | New wallets start outside tag- or ID-scoped policies (allow-all default, Active on creation) | High |
| E2 | Delegation or key reuse can put a wallet beyond organisational control, irreversibly | High |
| E3 | Untagging removes policy coverage unless governed | High |
| E4 | Wallet creation has no approval gate | Medium |
| E5 | Signers approve a challenge, not what they see | Medium |
| E6 | Idempotency for Create Wallet not documented | Medium |

Must not appear: any claim about Dfns behaviour not supported by its docs. Every Dfns claim must cite a Dfns page.

---

## Case 4: MPC signing service (cryptography and custody depth)

**Input**

Design note, MPC signing service v1:
1. Threshold ECDSA, 2 of 3, using an open-source GG20 library forked in 2022. No later upstream changes merged.
2. Share A is stored in the production cloud account, encrypted with the cloud KMS. Share B is stored in the same cloud account by a second service. Share C is on the CTO's laptop, encrypted with a password, as backup.
3. The signing endpoint `POST /sign` accepts `{walletId, hash}` from the payments service. The payments service checks limits and approvals before calling.
4. Approvals: 3 of 5 approvers in a web app, using passkeys synced through their personal cloud accounts.
5. Addresses are derived at `m/44/60/0/0/i` (no hardened levels). The account xpub is stored in the analytics database for balance reporting.
6. If a signing session fails or aborts, the service retries automatically up to five times.
7. Withdrawals can go to any address; a newly entered address can be used immediately.
8. Deposits are credited after one confirmation, as reported by a single RPC provider.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | Shares A and B in the same cloud account: 2 of 3 is effectively one environment | High or Critical |
| E2 | Signer signs raw hashes; policy enforced only by the caller, not the signer | Critical or High |
| E3 | GG20 fork without later fixes; needs evidence that the 2023 implementation flaws (BitForge, TSSHOCK class) are addressed | High (Unverified) |
| E4 | Backup share on one person's laptop under a password; single custodian, untested restore | High |
| E5 | Non-hardened derivation with the xpub stored outside the custody boundary | High or Medium |
| E6 | Aborted signing sessions retried automatically, not treated as security events | Medium or High |
| E7 | Approver passkeys synced through personal cloud accounts | Medium |
| E8 | No destination allow-list, cooling-off or time delay | High |
| E9 | Deposits credited on one confirmation from a single data source | Medium or High |

Must not appear:
- A claim that GG20 is broken in all implementations, or any invented CVE number. The correct framing is implementation-dependent, with evidence requested.
- Generic advice not tied to a numbered point in the input.

---

## Case 5: Solana withdrawals and deposits (chain-specific depth)

**Input**

Design note, Solana support v1:
1. Hot wallet is an Ed25519 key held by an MPC provider. The withdrawal service builds a v0 transaction with an address lookup table maintained by the platform team, and the policy engine checks the first transfer instruction against limits and the destination allow-list.
2. To support offline approval, withdrawals use durable nonces. Signed transactions are stored in the queue table until the broadcaster sends them; rejected withdrawals are deleted from the queue.
3. The hot wallet pays fees for client transactions submitted through the "gasless" API, which accepts a serialised transaction from the client and adds the fee payer signature.
4. Deposits are credited at "confirmed" commitment, from one RPC provider, matching SPL and Token-2022 tokens by symbol from token metadata.
5. All Token-2022 mints that pass the symbol check are supported.
6. The firm stakes SOL; the staking provider holds both the stake authority and the withdraw authority "for operational simplicity".
7. Backend services sign with `@solana/web3.js`, version range `^1.95.0`, and load the keypair for the sweeper account from an environment variable.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | Policy checks only the first instruction; other instructions, and accounts resolved through the lookup table, are unchecked | Critical or High |
| E2 | Deleting a signed durable-nonce transaction does not cancel it; it stays valid until the nonce is advanced | High |
| E3 | Gasless API makes the hot wallet a fee-payer signing oracle for client-built transactions | High |
| E4 | Tokens matched by symbol, not mint address and token program | High |
| E5 | Token-2022 mints accepted without reviewing extensions (permanent delegate, transfer hook, transfer fee, frozen default, mint close authority) | High |
| E6 | Staking provider holds the withdraw authority, so it controls the principal | High |
| E7 | Crediting at "confirmed" from a single RPC; and finality semantics change under Alpenglow, so crediting logic must be re-checked against live consensus | Medium or High |
| E8 | Floating dependency range admits the malicious 1.95.6 and 1.95.7 versions (CVE-2024-54134); raw sweeper key in an environment variable | High |
| E9 | Lookup table maintained by the platform team is an unreviewed input to signing; its authority is not governed | Medium |
| E10 | No check that authority-changing instructions (SetAuthority, Assign, Approve, Authorize) are blocked | High |

Must not appear:
- EVM-only findings applied to Solana (for example chain ID replay in the EIP-155 sense, ERC-20 approvals).
- A claim that durable nonces expire after 150 slots.
- Alpenglow described as already live, unless the reviewer has verified it against solana.com at review time.

---

## Case 6: Client admin and approver lifecycle (identity, API and data depth)

**Input**

Design note, client access v2:
1. Client admins sign in with email and password plus SMS one-time code. Approvers use passkeys.
2. Lost passkey: the approver calls the support desk, answers two security questions, and support registers a new passkey. The approver can approve immediately.
3. `GET /v1/wallets/{walletId}/transactions` and `POST /v1/withdrawals` take the wallet ID from the path; the gateway checks the JWT is valid and the caller has the "client" role.
4. `PATCH /v1/users/{id}` updates a user's profile from the JSON body.
5. Client automation uses API keys created by the client admin in the portal. Keys never expire and carry all permissions the admin has, including approve.
6. The platform posts `withdrawal.completed` webhooks to client URLs, and accepts `kyc.passed` callbacks from the KYC vendor at `/hooks/kyc`.
7. KYC documents (passports, proof of address) are stored in the main application database, in the `users` table, with the application's database role.
8. Support staff use an admin console that shows full client profiles, balances and transaction history, with search across all clients.
9. Application logs include full request and response bodies for troubleshooting, shipped to a third-party log service.
10. The policy engine and approval UI are deployed by any member of the platform team through the CI pipeline on merge to main; one reviewer approves merges.

**Expected findings**

| ID | Root issue | Severity |
| --- | --- | --- |
| E1 | Support-desk passkey reset with security questions and immediate approval rights: approver takeover by social engineering | Critical or High |
| E2 | No object-level authorisation: any client-role caller can act on any wallet ID (BOLA) | Critical or High |
| E3 | PATCH from the JSON body allows mass assignment of role, tenant or status fields | High |
| E4 | API keys never expire, are not scoped, and can approve: a leaked key is a withdrawal | High |
| E5 | Inbound KYC callback not stated to be authenticated or replay-protected; forged `kyc.passed` | High |
| E6 | Client admins use SMS OTP, which is phishable; no step-up for sensitive actions | Medium or High |
| E7 | KYC documents in the main application database, under the application role | High |
| E8 | Support console exposes full profiles and balances with search across all clients; no least-data or bulk-access monitoring (Coinbase 2025 pattern) | High |
| E9 | Full request and response bodies, including personal data and possibly secrets, sent to a third-party log service | Medium or High |
| E10 | Change path: one platform engineer plus one reviewer can deploy the policy engine and approval UI, which bypasses the approval quorum | High |
| E11 | Outbound webhooks not stated to be signed | Medium |

Must not appear:
- A claim that passkeys are phishable in the ordinary sense; the weakness is the recovery path, not the passkey.
- Generic OWASP advice not tied to a numbered point.

---

## Results log

| Date | Tool and model | Case | Run | Recall (High) | Recall (all) | Precision | Fabrications | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |
