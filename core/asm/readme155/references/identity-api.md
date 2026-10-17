# Identity, access and API lens

Apply to every flow with a human or machine caller: sign-in, sessions, roles, approvals, account and admin lifecycle, client APIs, webhooks, service-to-service calls, and any AI agent that can act. Onboarding, approval and recovery flows are where custody platforms are most often entered: attackers usually go after the person or the help desk, not the key.

## Authentication and sessions

| Check | Why it matters |
| --- | --- |
| Authentication strength matches the action: phishing-resistant MFA (WebAuthn, passkeys, smartcards) for admins, approvers and anyone who can change destinations, policies or users | Passwords and OTP are phished in real time |
| **Step-up authentication** for high-risk actions (new destination, policy change, approver change, large withdrawal, API key creation), bound to that action | A stolen session should not be enough to move funds |
| Tokens are validated fully: signature, issuer, audience, expiry, algorithm pinned; short lifetimes; refresh tokens rotated and revocable | Weak token validation lets one token work everywhere |
| Sessions are revoked on password, MFA or role change, and on suspected compromise | Old sessions outlive the change that was meant to stop them |
| Federation and SSO: who can change the identity provider configuration, and is it governed like a policy change | The IdP admin can become anyone |

## Account recovery and help desk

| Check | Why it matters |
| --- | --- |
| **Recovery and MFA reset are as strong as sign-in**, with identity proofing, a cooling-off period, notification to the user and to other admins, and no immediate high-risk rights afterwards | Recovery is the weakest path into most accounts |
| Help-desk and support staff cannot reset MFA, add approvers, change destinations or read full client data without a second person and an audit trail | Support staff are bribed or socially engineered; Coinbase disclosed in 2025 that overseas support staff were paid to take customer data, later used to scam customers (see incidents) |
| Support tooling shows the minimum client data needed | Bulk access in support tools turns one insider into a data breach |
| Clients are told how the firm will and will not contact them | Stolen client data is used to impersonate the firm |

## Authorisation (APIs and UIs)

| Check | Why it matters |
| --- | --- |
| **Object-level authorisation** on every request that takes an ID (wallet, vault, request, organisation, account): the caller's tenant and rights are checked against that object, server-side (OWASP API1, broken object level authorisation) | IDs in URLs are the most common API flaw; in custody it means acting on another client's wallet |
| Property-level authorisation: callers cannot set fields they should not (status, approver lists, limits, owner, tenant), and responses do not over-share (OWASP API3) | Mass assignment silently grants rights |
| Function-level authorisation: admin and staff endpoints are separated and checked, not just hidden (OWASP API5) | Hidden is not protected |
| Maker-checker is enforced server-side, including that the initiator is not an approver and approvers are distinct people, not distinct sessions | UI-only separation of duties is bypassed by calling the API |
| Edits after approval invalidate the approval | Approve-then-edit is a classic custody flaw |
| Role and entitlement changes are themselves approved, logged and alerted | Privilege changes are the attacker's first move |

## Client API keys, webhooks and integrations

| Check | Why it matters |
| --- | --- |
| Client API keys are scoped (read, initiate, approve kept separate), bound to IP allow-lists or mTLS where possible, expiring and rotatable; creating one needs step-up | A leaked key with initiate and approve rights is a withdrawal |
| An API key or service account can never satisfy a human approval quorum on its own | Automation must not become a silent approver |
| Rate and resource limits per caller and per action, including withdrawals, address creation and expensive queries (OWASP API4), and protection of sensitive business flows from automated abuse (OWASP API6) | Abuse, enumeration and cost attacks |
| Outbound webhooks are signed, timestamped and replay-protected; inbound callbacks from vendors are verified the same way | Forged callbacks can mark payments or KYC as complete |
| Outbound calls built from user input are restricted to allow-listed hosts (OWASP API7, server-side request forgery) | SSRF reaches internal services and cloud metadata |
| Third-party API responses are validated, not trusted (OWASP API10) | A compromised vendor feeds the platform |

## Service and workload identity

| Check | Why it matters |
| --- | --- |
| Each service has its own identity and least-privilege rights; no shared credentials across services or trust levels | Shared credentials make one compromise many |
| Calls to the signer and policy engine are mutually authenticated and authorised per operation | Any internal caller reaching the signer is a key holder |
| **Change path equals signing path:** whoever can deploy code or configuration to the signer, policy engine, approval UI or address book is counted as part of the custody control set, and those deployments need two-person approval | A malicious deployment bypasses every runtime control |

## AI agents and automation in the flow

Apply if an AI agent, LLM or automated workflow can read client data, prepare transactions, or initiate or approve actions.

| Check | Why it matters |
| --- | --- |
| The agent's output is treated as untrusted input: it can propose, never approve, and policy is enforced downstream of it | Prompt injection through documents, emails, web pages or memos can steer the agent |
| The agent's tools and credentials are scoped to the minimum, with per-action limits | An over-privileged agent is an insider that can be talked into anything |
| Content the agent reads (tickets, documents, on-chain memos, web pages) is assumed hostile | Injected instructions arrive through data, not through the user |
| Every agent action is attributable and logged with its inputs | Needed to investigate and to reverse what can be reversed |

## Sources

- [OWASP API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [Coinbase disclosure, The Register, 15 May 2025](https://www.theregister.com/2025/05/15/coinbase_extorted_for_20m_support/)
