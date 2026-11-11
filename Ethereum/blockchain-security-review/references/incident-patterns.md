# Attacker catalogue and incident patterns (Phase 3)

## Attacker catalogue

Apply each relevant attacker to each invariant.

- Compromised approver device or session
- Compromised UI, frontend or one of its dependencies
- Compromised initiator or API client
- Malicious insider, per role
- Colluding insiders below quorum
- Compromised CI/CD pipeline or software dependency
- Cloud or infrastructure administrator
- k-1 compromised MPC nodes or HSM partitions
- Vendor or custodian compromise
- State-level actor targeting staff (fake recruiters, planted contractors, long social-engineering campaigns)
- Lying or stale RPC node
- False oracle, price or reserve attestation
- Malicious contract upgrade
- Economically rational attacker with flash liquidity
- MEV searcher, builder or sequencer
- Byzantine validators up to, and just beyond, the stated threshold
- Network attacker: drop, delay, reorder, replay, eclipse, partition
- Malicious prover or malicious verifier
- Malicious or compromised counterparty chain
- Physical access to backups or devices
- Future quantum adversary against long-lived keys and recorded ciphertext

## Incident pattern check

Baseline list; extend it with Phase 0B results. For each pattern relevant to the system class, cite the control that prevents it in this design, or raise a finding. Dates are for orientation; confirm against a Tier 1 or Tier 2 source before quoting one in a report.

**Signing and custody**
- Blind signing through a compromised shared UI or signer devices: Bybit (2025), Radiant Capital (2024), WazirX (2024)
- Quorum concentrated under one operator or too small: Ronin (2022), Harmony Horizon (2022)
- Key material centralised with one person or server: Multichain (2023)
- Threshold-ECDSA implementation flaws: TSSHOCK and BitForge (2023)
- Nonce reuse or bias leaking private keys
- Weak key-generation entropy: Profanity vanity addresses (2022)
- Seed or key material written to logs or telemetry: Slope wallet (2022)
- Supply-chain compromise of wallet libraries: Ledger Connect Kit (2023); DNS and frontend hijacks

**Bridges**
- Verifier bypass on the destination: Wormhole (2022)
- Unsafe initialisation accepting any message: Nomad (2022)
- Privileged cross-chain call changing the verifier set: Poly Network (2021)

**Contracts and DeFi**
- Unprotected library or implementation contract: Parity multisig (2017)
- Reentrancy: The DAO (2016); read-only reentrancy through Curve `get_virtual_price` (disclosed 2022, exploited at dForce in 2023)
- Compiler bug breaking a reentrancy guard: Vyper (2023)
- Price-oracle manipulation with flash liquidity: Mango Markets (2022)
- Governance takeover by flash loan: Beanstalk (2022)
- First-depositor share inflation, donation and rounding attacks (recurring)
- Unbacked mint through an admin or upgrade path
- Algorithmic peg collapse: Terra (2022)

**Zero knowledge**
- Weak Fiat-Shamir transformation: "Frozen Heart" (2022)
- Under-constrained circuits: the largest class in the ZK Bug Tracker and the 2024 SNARK vulnerability study
- Soundness bug allowing counterfeiting: Zcash (found 2018, disclosed 2019)

**Protocols and clients**
- Loss of finality from client bugs under load: Ethereum (May 2023)
- Consensus-critical implementation bugs: Bitcoin value overflow (2010), CVE-2018-17144 (2018)
- Network halts from resource exhaustion or client faults (several chains)

## Mapping

Where useful, map notable attack paths to MITRE AADAPT and ATT&CK technique IDs fetched in Phase 0B, so findings line up with the organisation's threat intelligence.
