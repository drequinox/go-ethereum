Here’s a prompt that strikes the balance between comprehensive and maintainable:

Act as a principal security architect and distributed systems engineer designing a next-generation institutional digital asset custody platform from first principles. Produce a technology-only requirements specification using RFC 2119/RFC 8174 normative language (MUST, MUST NOT, SHOULD, MAY). Focus on architecture-level, implementation-independent requirements rather than low-level design decisions. The platform must be fully homegrown with no dependency on third-party custody or wallet providers, while remaining vendor-agnostic and extensible. Cover: Architecture, Cryptography & Key Management, Identity & Access Management, Wallet Management, Transaction Processing, Blockchain Integration, Security Controls, APIs & External Interfaces, Audit & Logging, Monitoring & Observability, Resilience & Disaster Recovery, Non-Functional Requirements, and Testing & Verification. For each section, produce concise, atomic, testable requirements with unique IDs. Avoid business, regulatory and product-management requirements. Use public documentation from platforms such as Fireblocks, Dfns and other leading institutional custody solutions only as inspiration for capabilities and best practices—never copy their architecture or terminology. The resulting specification should be comprehensive enough for an enterprise engineering team to build the platform, yet concise, maintainable and technology-agnostic.


Yes—absolutely use Fireblocks, Dfns and other custody platforms for inspiration. Since you are building a fully homegrown platform, treat them as:

* capability benchmarks;
* threat-model inputs;
* API and workflow references;
* sources of failure cases and design trade-offs.

Do not structure your requirements as “replicate Fireblocks.” Your specification should remain independent of any vendor’s terminology, architecture or cryptographic scheme.

What to study

Fireblocks and Dfns publicly expose enough documentation to understand their major architectural concepts. Fireblocks documents hot, warm and cold wallet models, MPC-based signing, policy-controlled transaction authorisation and transaction state management. 

Dfns is particularly useful for studying separation between authentication credentials, wallet keys, permissions, policies and signing infrastructure. Its documentation describes MPC signing, API authentication, policy evaluation, wallet and key abstractions, and layered governance. 

Extract inspiration from areas such as:

* wallet and key abstractions;
* transaction state machines;
* policy engines;
* approval workflows;
* authentication versus signing separation;
* MPC or HSM signing boundaries;
* raw signing versus managed transfers;
* address allowlisting;
* fee and gas management;
* blockchain adapters;
* API idempotency;
* audit trails;
* emergency suspension;
* hot, warm and cold custody tiers.

Do not copy their architecture blindly

Their platforms solve somewhat different problems and embed vendor-specific assumptions.

For example, Fireblocks’ wallet tiers are partly distinguished by the location and operation of MPC shares. Dfns separates wallet authentication credentials from wallet signing keys and supports different transaction paths, including managed transfers, sign-and-broadcast and raw signing. 

Your architecture should instead derive from explicit security invariants such as:

No single compromised person, application, host or administrative domain MUST be sufficient to move assets.

Authentication approval and cryptographic signing MUST occur through independently protected control paths.

The signing subsystem MUST independently validate transaction intent rather than trusting the orchestration layer.

Loss or compromise of the orchestration platform MUST NOT expose private-key material.

These invariants may lead you towards MPC, HSM-backed signing, multisignature or a hybrid architecture. The requirements should not assume the answer prematurely.

The right benchmarking method

Create a small capability comparison matrix, not an enormous feature inventory:

Capability	Fireblocks	Dfns	Homegrown requirement
Wallet abstraction	Vault and asset wallets	Wallet and key objects	Define your own wallet domain model
Key protection	MPC-based models	MPC and documented HSM deployment options	Pluggable signing boundary
Transaction controls	Policy-controlled authorisation	Permissions and policy engine	Deterministic policy evaluation
Transaction paths	Managed custody workflows and raw signing	Transfer, sign-and-broadcast and raw signing	Separate intent, signing and broadcast APIs
Identity	Users and API identities	Passkeys and signed service-account requests	Enterprise IAM plus workload identity
Wallet tiers	Hot, warm and cold	Deployment-dependent signing model	Risk-tiered custody profiles
Auditability	Transaction and approval states	Authentication, policy and signing records	End-to-end cryptographic evidence

Dfns’ API also distinguishes wallets from underlying keys and permits controlled key reuse across wallets, which is a useful domain-modelling question even if you ultimately reject that approach. 

Homegrown does not mean literally zero external dependencies

You can eliminate custody-vendor dependency, but a production platform cannot realistically contain no third-party components whatsoever. You will still depend on some combination of:

* cryptographic libraries;
* operating systems;
* databases and message brokers;
* HSM firmware or hardware;
* blockchain clients;
* cloud or data-centre infrastructure;
* identity infrastructure;
* monitoring systems;
* open-source libraries.

The more useful requirement is:

The platform MUST NOT depend on an external custody, wallet-as-a-service, signing or transaction-policy provider for continued control or recovery of assets.

And:

The institution MUST retain sufficient cryptographic material, software, configuration, records and operational procedures to operate, recover and migrate the custody platform without cooperation from a custody-platform vendor.

Recommended sweet-spot structure

For your homegrown requirements document, I would keep these 14 technical sections:

1. Scope and normative conventions
2. Architecture and trust boundaries
3. Threat model and security invariants
4. Cryptography and key management
5. Identity and authorisation
6. Wallet and address management
7. Transaction and policy processing
8. Signing subsystem
9. Blockchain and token integration
10. APIs and data integrity
11. Audit, monitoring and incident controls
12. Infrastructure security and resilience
13. Non-functional requirements
14. Testing and conformance

Use Fireblocks, Dfns and perhaps three or four other systems to check whether you have missed a major capability. Do not add a requirement merely because a vendor exposes a feature. Add it only when it follows from your use cases, threat model or security invariants.

The best framing is:

Vendor-informed, but vendor-independent. Built from first principles, benchmarked against established custody platforms, and designed so that institutional control of assets never depends on an external custody provider.