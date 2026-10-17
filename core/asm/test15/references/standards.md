# Standards and framework mapping

Map findings to frameworks only where it adds weight for risk, audit or regulatory readers. Cite the framework and the family or area. **Do not cite specific control numbers unless you are certain of them for the current version; when unsure, cite the family and say "confirm control reference".** Invented control IDs destroy credibility.

| Framework | Use it for | Typical mapping |
| --- | --- | --- |
| CryptoCurrency Security Standard (CCSS) | Custody-specific controls: key generation, storage, usage, compromise policy, audits | Key lifecycle, quorum, backup and recovery findings |
| NIST Cybersecurity Framework 2.0 | Board and risk-level framing across Govern, Identify, Protect, Detect, Respond, Recover | Summary-level mapping of themes |
| NIST SP 800-57 | Key management practice: lifecycle states, key hierarchy, rotation | Cryptography and backup findings |
| FIPS 140-3 | Cryptographic module validation (FIPS 140-2 certificates moved to the historical list in September 2026) | HSM and module findings |
| NIST post-quantum standards FIPS 203, 204, 205 | Post-quantum migration planning | Crypto agility findings |
| OWASP ASVS (version 5.0 released 2025) | Application-level verification requirements | Authentication, session, access control, API findings |
| OWASP API Security Top 10 | API-specific risk categories | Authorisation and object-level access findings |
| ISO/IEC 27001:2022 and SOC 2 | Organisational control environment | Access management, change management, supplier findings |
| EU DORA (applies from January 2025) | ICT risk, incident reporting, third-party risk, resilience testing for EU financial entities | Vendor dependency, incident response, resilience findings |
| EU MiCA | Crypto-asset service provider obligations, including custody and segregation | Client asset segregation and custody policy findings |
| FATF Recommendation 16 (travel rule) | Originator and beneficiary information on transfers | Compliance gating findings |

Add the firm's internal control framework and policy references when the user provides them; they usually carry more weight internally than external standards.

## Sources for dates and versions above

Checked on 17 October 2026. Standards and regulations change; re-check before citing a date or version in a deliverable, per the external verification rule in SKILL.md.

| Fact | Source |
| --- | --- |
| FIPS 140-2 certificates move to the historical list on 21 September 2026 | [SafeLogic](https://www.safelogic.com/blog/what-happens-on-september-21-2026) |
| FIPS 203, 204 and 205 approved August 2024 | [NIST announcement](https://www.nist.gov/news-events/news/2024/08/announcing-approval-three-federal-information-processing-standards-fips) |
| OWASP ASVS 5.0 released 2025 | [OWASP ASVS project](https://owasp.org/www-project-ASVS/) |
| DORA applies from 17 January 2025 | [De Nederlandsche Bank](https://dnb.nl/en/sector-information/open-book-supervision/laws-and-eu-regulations/dora) |
| MiCA fully applicable from 30 December 2024 | [K&L Gates](https://www.klgates.com/The-Regulation-on-Markets-in-Crypto-Assets-Becomes-Fully-Applicable-in-All-Member-States-of-the-European-Union-1-24-2025) |
