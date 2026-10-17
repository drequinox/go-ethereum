# Data protection and privacy lens

Apply to any flow that collects, stores or shares personal or client data: onboarding and KYC or KYB, user and approver records, transaction history, travel-rule data, support tooling, analytics and logs. Client data in custody is valuable on its own: it is used to target clients and staff with social engineering, and to locate holders of large balances.

| Check | Why it matters |
| --- | --- |
| Data is classified, and each store and flow records which classes it holds (KYC documents, identity data, balances, addresses linked to identities, approver details) | You cannot protect data you have not located |
| Collection is minimised to what the purpose needs; retention periods are defined and enforced, including in backups and logs | Data kept is data that can leak |
| Identity documents and KYC data sit in a separate store with its own access control, encryption keys and access logging, not in the main application database | One application compromise should not expose every client's identity documents |
| Linking of on-chain addresses to identities is restricted and logged | That link turns public blockchain data into a target list |
| Secrets and personal data are excluded from logs, traces, error reports, analytics and crash reporting by design, and this is tested | Telemetry has leaked seed phrases (Slope) and customer data |
| Data residency is respected by every store, backup, vendor and support location, per tenant or region where promised | Residency promises break in replicas, backups and offshore support |
| Vendors receiving personal data (KYC, KYT, analytics, support, cloud) are listed with purpose and contract terms | Each vendor is another breach surface |
| Access to personal data by staff and support is need-to-know, time-bound for bulk access, and monitored for unusual volume | Insider exfiltration is usually bulk and visible, if anyone looks |
| A data protection impact assessment is triggered where the law requires one (for example under UK and EU GDPR for high-risk processing) | A regulatory requirement, and a useful review input |
| Deletion and offboarding remove or anonymise data across systems, subject to record-keeping duties | Offboarded clients' data lingers |
| Travel-rule exchanges send only the required fields, over authenticated channels, to verified counterparties | Travel-rule data is personal data sent to third parties |

## Sources

- [UK ICO: data protection impact assessments](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/)
- [The Block on Slope (seed phrases sent to a Sentry server)](https://www.theblock.co/post/161425/slope-wallet-provider-saved-user-seed-phrases-in-plain-text-solana-security-researchers-find)
