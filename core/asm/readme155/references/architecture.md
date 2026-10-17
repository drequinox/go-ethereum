# Software architecture lens

Security reviews that ignore architecture miss the cause of many security findings: unsafe async states, hidden coupling, missing failure paths. This lens is a light version of the SEI Architecture Tradeoff Analysis Method (ATAM): quality attribute scenarios, sensitivity points, trade-offs and risks.

## Quality attribute scenarios

Write three to six scenarios for the attributes that matter most to this system. Format each as: source, stimulus, environment, response, response measure. Example:

> Peak withdrawal day (environment): 5,000 withdrawal requests in an hour (stimulus) from clients (source). The signing service processes them (response) with 95% signed within 10 minutes and no request signed twice (measure).

For each scenario, state whether the design meets it, misses it, or the inputs do not say.

| Attribute | Typical concern in custody and payment systems |
| --- | --- |
| Correctness and consistency | Ledger and chain agree; no duplicate or lost transfers under retries and partial failures |
| Availability of signing | Time to restore signing after loss of a signer, region or vendor (RTO), and data loss tolerance (RPO, normally zero for keys and approvals) |
| Performance and capacity | Signing throughput and latency of HSM or MPC under peak; queue behaviour when saturated |
| Recoverability | Restore of keys, approvals and ledger from backup, rehearsed |
| Operability | Ceremonies, rotations and incident actions are executable by the team in the time required |
| Observability | Every state transition and signing event is traceable end to end |
| Modifiability | Policies, chains and assets can be added without weakening existing controls |
| Isolation | Tenants, environments (testnet and mainnet) and wallet tiers cannot affect each other |

## Architecture checks

| Check | Why it matters |
| --- | --- |
| Every multi-step write is atomic or uses a defined pattern (transactional outbox, saga with compensation) | Partial writes produce unsafe intermediate states |
| Every async consumer is idempotent and the state while a message is in flight is safe | At-least-once delivery means duplicates; delays mean windows |
| State machines are explicit, with transitions enforced in one place | Scattered checks drift apart |
| No single point of failure in the signing path without a documented, rehearsed failover | A signer outage invites unsafe manual workarounds |
| Dependencies are mapped, and the behaviour when each is down is designed (fail closed for security decisions) | Undesigned fallbacks tend to fail open |
| Services do not share databases or credentials across trust levels | Shared stores collapse trust boundaries |
| Environments are separated: testnet and mainnet keys, credentials and signers never mix | Test tooling with mainnet reach is a common accident |
| Configuration that grants rights (policies, roles, allow-lists) is versioned, reviewed and deployed like code | Untracked configuration changes are invisible control changes |
| Interfaces between components are versioned, including approval and signing payload formats | Format changes can silently break binding between approval and execution |
| Capacity is planned for peak events (market stress, incident-driven withdrawals) | Stress events are when controls get bypassed |

## Output: architecture assessment (Template C section 9)

1. Quality attribute scenarios with Met, Missed or Unknown.
2. Sensitivity points: design decisions that strongly affect one attribute (for example "policy binding via async event affects correctness and security").
3. Trade-offs: decisions that help one attribute and hurt another, with a recommendation.
4. Architecture risks: findings that are not security vulnerabilities but threaten correctness, resilience or operability. Give them IDs in the same sequence and rate them on the same rubric, using impact on the business.
