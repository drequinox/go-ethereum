# Blockchain and transaction lens

Apply to transaction construction, signing payloads, deposits and withdrawals, node and indexer use, smart contracts, tokens, bridges, staking and account abstraction. Chain behaviour differs; do not assume one chain's properties for another. When unsure of a chain-specific detail, ask.

## Transaction lifecycle

| Check | Why it matters |
| --- | --- |
| Transactions are built by a trusted component from validated parameters, not accepted pre-built from callers | Pre-built transactions hide their effect |
| Nonce or sequence numbers are allocated centrally and safely under concurrency and retries | Gaps stall withdrawals; reuse replaces transactions |
| Fee settings have ceilings, and replacement (speed-up or cancel) is governed like a new transaction | Fee manipulation and replacement can redirect value or drain funds through fees |
| Signed transactions are stored and broadcast idempotently; resubmission cannot double-spend on account-based chains | Retries must not create a second transfer |
| Replay protection is in place across chains and forks (chain ID or equivalent) | Signatures valid on one network must not be valid on another |
| Broadcast uses more than one route or provider for critical payments | Node censorship or outage delays settlement |

## Deposits and finality

| Check | Why it matters |
| --- | --- |
| Deposits are credited only after the chain-appropriate finality or confirmation depth, per asset and amount | Reorgs and double spends reverse unfinalised deposits |
| Deposit detection is checked against more than one independent data source, or own nodes | A compromised or faulty RPC provider can report deposits that never happened |
| Token deposits are verified against the canonical contract address, not the token name or symbol | Fake tokens with real names are common |
| Non-standard token behaviour (fee on transfer, rebasing, pausable, blocklists) is handled per asset | Ledger and chain diverge otherwise |
| Unsolicited inbound transfers (dust, poisoning, airdrops) are quarantined and not auto-credited or auto-swept | They are used for poisoning and for tainting wallets |

## Address integrity

| Check | Why it matters |
| --- | --- |
| Addresses are derived or verified independently before they are shown to clients | A compromised service can display an attacker's address |
| Full-address comparison and checksum validation, with alerts for look-alikes of known counterparties | Address poisoning relies on users checking only the start and end |
| Address book entries are dual-controlled | The address book is itself an attack target |

## Smart contracts (multisig wallets, vaults, tokens, custody contracts)

| Check | Why it matters |
| --- | --- |
| Contracts in the custody path are audited, with the audited version matching the deployed bytecode | Audits of a different version give false assurance |
| Upgradeable contracts: who controls upgrades, with what threshold and time delay | The upgrade key is the master key |
| Calls that change ownership, modules, guards, implementation or that use delegatecall are blocked or require elevated approval | One such call can hand over the whole wallet |
| Token approvals and permit or permit2 signatures are bounded in amount and time, and monitored | Signed approvals are a common theft route that needs no transaction from the victim |
| Contract interactions are allow-listed by contract address and function for each wallet | Limits what a compromised signer can be induced to do |
| Emergency pause or guard mechanisms exist and are governed | Allows containment while an incident is assessed |

## Bridges, cross-chain and layer 2

| Check | Why it matters |
| --- | --- |
| The trust model of each bridge or messaging protocol is documented: who can mint or release, with what threshold | Bridges have been the largest single category of loss |
| Exposure to any one bridge is limited | Bridge failure is binary and often total |
| Withdrawal periods and finality of layer 2 networks are accounted for in liquidity and crediting | Funds may be locked or reversible for longer than expected |

## Staking and protocol participation

| Check | Why it matters |
| --- | --- |
| Validator keys are separated from withdrawal or custody keys | Validator infrastructure is online and more exposed |
| Slashing risk (double signing, downtime) is controlled: no duplicate validators, failover that cannot double sign | Slashing destroys principal |
| Withdrawal credentials point to custody-controlled addresses and cannot be changed by the operator | Otherwise the staking provider controls the principal |

## Account abstraction and programmable wallets

| Check | Why it matters |
| --- | --- |
| Validation logic, paymasters and modules are audited and governed like any custody contract | Validation logic is the new authorisation layer |
| Session keys and delegated permissions are scoped and expire | Unbounded delegations are standing backdoors |

## Compliance on-chain

| Check | Why it matters |
| --- | --- |
| KYT or sanctions screening covers both inbound and outbound flows, before signing for outbound | Sending to a sanctioned address is a regulatory breach that cannot be reversed |
| Travel-rule data is attached where required and the transfer fails closed if it cannot be exchanged | Missing data is a compliance failure |
| Screening provider outages fail closed for outbound transfers | Fail-open screening is no screening |
