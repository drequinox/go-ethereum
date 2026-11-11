# Invariant packs (Phase 2)

Select packs by the profiles classified in Phase 0. Tailor each invariant to the system, drop what is out of scope, add system-specific invariants, and apply Phase 0B updates. Each invariant is a property that must hold in every reachable state.

Contents: K keys · S signing · W wallets · M mint/burn · B bridges · C contracts · D DeFi · O oracles · P protocol/consensus · N node/network · R rollups/L2 · Z zero knowledge · X cryptography · E enterprise DLT · V staking · T exchange/settlement · G governance/operations

## K: Key lifecycle
- K1 Key material, or a full reconstruction of it, never exists in plaintext outside the HSM/MPC/enclave boundary, including during generation, backup, recovery and migration.
- K2 No single party (person, node, tenant, admin, vendor) can produce a valid signature.
- K3 Keys come from verified entropy; DKG is verifiable; libraries are patched against known threshold-signature attacks; nonces are never reused or biased.
- K4 Recovery and resharing need a quorum at least as strong as signing; old shares are invalidated.
- K5 HSM keys are non-extractable (`CKA_EXTRACTABLE=false`, `CKA_SENSITIVE=true`); wrapping keys are equally protected; permitted mechanisms are restricted.
- K6 Keyholder grant and revoke are quorum-controlled and take effect before a departing holder can act.
- K7 Backups are encrypted, geographically separated, tested, and cannot be combined below quorum.
- K8 Key derivation (BIP-32/39/44, SLIP-10) uses hardened paths where a child-key leak must not expose parents; xpub exposure is understood; seed handling is documented.
- K9 Enclave or TEE trust: attestation is verified; rollback and side-channel exposure are considered; the enclave is not the only barrier where avoidable.

## S: Signing and approval
- S1 Signed bytes equal approved bytes; the approval binds the canonical hash, chainId, nonce, target, calldata, value and expiry.
- S2 Policy evaluates the decoded payload, never initiator-supplied metadata.
- S3 Each approver sees an independently decoded payload, produced outside the initiator's control path, on a trusted display.
- S4 One approval yields at most one signature and one execution.
- S5 No time-of-check/time-of-use gap between policy check and signing; the signer verifies a policy attestation over the same hash.
- S6 High-risk operation classes (delegatecall, approve/permit, role or ownership change, upgrade, arbitrary message or typed-data signing, account delegation) need elevated policy or are blocked.
- S7 Allow-list changes are quorum-approved and time-delayed; an address cannot be added and used in one step.
- S8 Velocity and value limits are enforced by a component the initiator cannot influence.
- S9 Automated signers and agents have scoped keys, hard limits and a kill switch; no human-free path to unlimited value.
- S10 Simulation or pre-execution results shown to approvers come from a source independent of the initiator.

## W: Wallet applications and user-side security
- W1 Seed and keys never leave the secure element or keystore unencrypted; no exposure through logs, analytics, clipboard or screenshots.
- W2 What the user sees is what is signed (clear signing; blind signing off by default); typed-data and permit requests are decoded.
- W3 dApp connections, deep links and wallet-connection sessions are bound to an origin; no silent session reuse.
- W4 Address integrity: poisoning, homoglyph, clipboard-swap and QR substitution are resisted.
- W5 Update and dependency supply chain is signed and pinned; remote configuration cannot change signing behaviour.
- W6 Backup and recovery (cloud backup, social recovery, passkeys) cannot be completed through one compromised account or provider.
- W7 Hardware wallets: attested firmware, deterministic or anti-exfiltration nonces, sound PIN and passphrase handling, evil-maid resistance.

## M: Mint, burn, issuance
- M1 totalSupply equals verified mints minus verified burns, reconciled to reserves.
- M2 Each backing event is consumable exactly once, enforced at every hop that can re-trigger signing, ideally on-chain.
- M3 Fiat or collateral is released only after burn finality; reorg depth is defined.
- M4 Minter, approver and custodian are separated; no role can grant itself mint rights.
- M5 Proxy admin, role admin and `DEFAULT_ADMIN_ROLE` holders are treated as mint authority.
- M6 Caps, rate limits, pause and freeze are under a quorum distinct from minting.
- M7 Reserve attestations are authenticated, fresh and independently sourced.
- M8 Freeze, seize and blocklist powers are bounded, logged and cannot be used to mint or redirect funds.
- M9 Multi-chain issuance: supply is conserved across chains; compromise of one chain cannot inflate another beyond a set limit.

## B: Bridges and cross-chain
- B1 A message executes on the destination only if finalised on the source, exactly once.
- B2 The verifier set (validators, guardians, light client, proof verifier) cannot be changed below its own security threshold; initialisation cannot be re-run or left at defaults.
- B3 Message authentication binds source chain, destination chain, contract, nonce and payload.
- B4 Locked and minted supply are conserved across chains.
- B5 Relayers are untrusted for safety (liveness only).
- B6 Rate limits and circuit breakers bound the loss per time window.
- B7 Light-client or proof verification handles source-chain reorgs, validator-set rotation and long-range attacks.
- B8 The trust assumption is stated plainly (who can steal, who can freeze) and matches the value at risk.

## C: Smart contracts and smart-contract wallets
- C1 Complete role and privilege inventory; every privileged function has a named, quorum-controlled holder.
- C2 Upgrades are time-locked, quorum-approved and storage-layout safe; implementation contracts are initialised and cannot be destroyed.
- C3 Signature validation is replay-safe (nonce, chainId, contract address, EIP-712 domain) and malleability-safe; contract-signature (ERC-1271) paths are checked.
- C4 External calls cannot re-enter or redirect control, including cross-contract and read-only reentrancy; installing modules, guards, hooks or plugins is privileged.
- C5 Account-abstraction paths (paymasters, session keys, bundlers, delegation) cannot exceed the owner's policy.
- C6 Deployed bytecode matches audited source; the compiler version is free of relevant known bugs.
- C7 Arithmetic: rounding favours the protocol, precision loss is bounded, unchecked and assembly blocks cannot overflow.
- C8 Token handling tolerates non-standard tokens (fee-on-transfer, rebasing, missing return values, transfer hooks, pausable, upgradeable).
- C9 No security decision rests on `tx.origin`, block values or other manipulable inputs; randomness comes from a sound source.
- C10 Denial of service: no unbounded loops, griefable external calls or lockable funds.
- C11 Platform-specific rules are applied (`references/chain-specifics.md`).

## D: DeFi and economic security
- D1 Solvency: assets cover liabilities in every reachable state, including after liquidations and bad debt.
- D2 Share and accounting invariants hold: no first-depositor inflation, donation attack or exchange-rate manipulation within one transaction.
- D3 No profitable manipulation within one block or with flash liquidity; cost of attack exceeds profit.
- D4 Liquidations stay possible and incentivised under congestion and price gaps.
- D5 Governance cannot be captured cheaply (flash-loan voting, low quorum, no timelock); parameter changes are bounded.
- D6 MEV exposure (sandwiching, back-running, oracle-update racing, just-in-time liquidity) is understood and bounded; slippage and deadline controls are enforced.
- D7 Composability: every external protocol dependency is listed with what happens if it pauses, depegs, upgrades or is exploited.
- D8 Restaking and liquid staking: slashing propagation and withdrawal queues cannot silently break peg or solvency assumptions.

## O: Oracles
- O1 Price and data sources resist manipulation for the value they secure (no spot-price reliance; averaging windows sized to liquidity).
- O2 Staleness, deviation, sequencer-uptime and decimal checks are enforced.
- O3 The oracle failure mode is defined (pause or fallback) and the fallback is not weaker.
- O4 Oracle update authority and aggregation threshold match the value at risk.

## P: Layer 1 protocol and consensus
- P1 Safety: no two conflicting blocks or states are finalised while the adversary is within the stated threshold; a proof exists and matches the implemented protocol.
- P2 Liveness holds under the stated synchrony model; behaviour during asynchrony and recovery is defined.
- P3 Accountability: safety violations yield slashable evidence; slashing cannot be triggered against honest validators.
- P4 Fork choice resists reorg, balancing, withholding and long-range attacks; weak-subjectivity or checkpoint rules are defined.
- P5 Leader and committee selection randomness is unbiasable and unpredictable to the degree required.
- P6 Validator-set changes, epoch boundaries and upgrades preserve safety.
- P7 Economic security: cost to attack versus value secured; honest behaviour is a best response; selfish mining, bribery and censorship strategies are analysed.
- P8 The state transition function is deterministic across implementations; resource metering prevents denial of service; mempool and fee market cannot be cheaply spammed or censored.
- P9 Client diversity: a bug in one implementation cannot finalise an invalid chain.
- P10 Time, clock and timestamp assumptions are bounded.
- P11 Genesis, initial distribution and any trusted setup are documented.
- P12 Cryptographic agility and a post-quantum migration path exist.

## N: Node, network and infrastructure
- N1 The P2P layer resists eclipse, Sybil, partition and amplification; peer scoring cannot be gamed to isolate validators.
- N2 RPC, admin and engine APIs are authenticated and not exposed; signing endpoints are unreachable from public networks.
- N3 A lying or stale RPC cannot cause a harmful signature or credit (several providers, proofs, or own nodes).
- N4 Validator and node keys are protected; remote signers carry slashing protection.
- N5 State sync, snapshots and checkpoints are verified.
- N6 Infrastructure concentration (cloud, region, provider) cannot halt or fork the system.
- N7 Indexers, explorers and off-chain databases used for decisions are verified against chain state.

## R: Rollups, L2, data availability
- R1 The operator or sequencer can only censor or delay, not steal or freeze; forced inclusion and exit work without operator cooperation.
- R2 State roots are accepted only with a verified validity proof, or after a live, permissionless challenge window of adequate length.
- R3 Data availability: state is reconstructible from published data; any alternative-DA trust assumption is stated and, where claimed, verified on-chain.
- R4 Upgrade keys, verifier keys and security-council powers are quorum-controlled, with an exit window longer than the upgrade delay (assess against the current L2BEAT Stages text).
- R5 Validity rollups satisfy pack Z; optimistic rollups have a complete, resource-bounded fraud-proof game.
- R6 L1/L2 messaging is replay-safe and reorg-safe; shared sequencing and interoperability preserve any atomicity claimed.
- R7 Sequencer MEV and pre-confirmation trust are stated.

## Z: Zero-knowledge proof systems
Use with `references/zk-review.md`.
- Z1 Soundness: no proof verifies for a false statement. The circuit is not under-constrained; every witness value used is constrained; assignments are distinguished from constraints.
- Z2 Completeness: every valid statement is provable (no over-constraint that freezes funds or exits).
- Z3 Zero knowledge: proofs and public inputs leak nothing beyond the statement; blinding is present; prover side channels are considered.
- Z4 The statement proved is the statement needed: specification-to-circuit equivalence; public inputs bind all context (chain, contract, nullifier, recipient, amount, epoch).
- Z5 Field arithmetic: range checks, bit-length checks, overflow and aliasing, non-native field emulation, division and inverse edge cases.
- Z6 Determinism: no witness freedom lets a prover choose among valid assignments with different meaning (nullifier uniqueness).
- Z7 Fiat-Shamir: the transcript includes all public inputs, the statement and prior messages, with domain separation; no partial hashing.
- Z8 Setup: ceremony integrity, participant count, toxic-waste assumption, parameter provenance; universal versus circuit-specific.
- Z9 Parameters deliver the claimed security level (curve, field size, query counts and proximity assumptions, hash choice, lookup soundness error); proven versus conjectured soundness is stated.
- Z10 The verifier, on-chain and off-chain, implements the protocol exactly: subgroup and on-curve checks, pairing inputs, public-input encoding and range, malleability, verification-key binding and upgrade control.
- Z11 Recursion, aggregation and folding: inner verification is fully constrained; deferred checks are discharged.
- Z12 zkVM and zkEVM: instruction semantics match the specified machine; memory, lookup and precompile constraints are complete; prover hints are constrained.
- Z13 Application layer: nullifier and commitment schemes prevent double-spend and linkability; Merkle roots are fresh; proofs cannot be replayed across contexts; relayers cannot front-run.
- Z14 Toolchain: compiler, DSL and framework versions are free of known bugs; the optimiser cannot drop constraints; circuit libraries are audited.

## X: Cryptographic design and primitives
- X1 Every primitive, parameter, curve and library is named with its version; none is deprecated or below the target security level.
- X2 A security proof exists for the scheme as used, and its model (adversary, corruption, composition, concurrency) matches deployment.
- X3 Domain separation for every hash and signature use; unambiguous encoding; no key reuse across protocols.
- X4 Randomness and nonces: sound generation, no reuse, deterministic or hedged where appropriate.
- X5 Signatures: malleability handled; BLS aggregation uses proof of possession or an equivalent defence against rogue-key attacks; Schnorr multi-signature and threshold schemes (MuSig, FROST) handle nonces safely under concurrent sessions; ECDSA low-s and recovery-id handling; consistent EdDSA variant.
- X6 Threshold and MPC protocols: defined behaviour on malicious parties (identifiable abort where claimed); proactive refresh; zero-knowledge sub-proofs present and correctly parameterised.
- X7 Encryption is authenticated; key and nonce management is sound.
- X8 Commitments, Merkle structures and accumulators: second-preimage and leaf/internal-node confusion prevented; proofs bound to root and index.
- X9 VRF, VDF and randomness beacons: unbiasability and unpredictability hold under the stated threshold.
- X10 Implementation: constant-time code, input validation (on-curve, subgroup), zeroisation, side-channel and fault resistance for hardware.
- X11 Post-quantum: inventory of quantum-vulnerable keys and long-lived secrets; harvest-now-decrypt-later exposure; migration plan to standardised post-quantum schemes.

## E: Enterprise and permissioned DLT
- E1 Membership: identity issuance, certificate authority and revocation are quorum-controlled; no single member or operator can admit or impersonate participants.
- E2 The ordering or consensus service cannot equivocate or censor undetected under the stated fault model; operator concentration is disclosed.
- E3 Endorsement, notary or validation policies cannot be satisfied by one organisation for multi-party assets.
- E4 Privacy: private data, privacy groups, channels or sub-transactions do not leak through ordering metadata, hashes of low-entropy data, shared nodes or logs; deletion and retention are defined.
- E5 Contract lifecycle and upgrade need multi-party approval; non-determinism is excluded.
- E6 Finality and settlement assumptions (legal and operational) are documented; reconciliation with off-ledger systems exists.
- E7 Node, key and API security at each participant meets a minimum bar; one weak member cannot compromise shared state.
- E8 Interoperation with public chains inherits packs B and N.

## V: Staking and validator operations
- V1 No double-signing: durable, single-writer slashing protection; failover cannot run two signers.
- V2 Withdrawal credentials and fee recipients are set once, independently verified, and cannot be redirected by an operator.
- V3 Validator keys and withdrawal keys are separated.
- V4 Exits and withdrawals are authorised by the asset owner; pre-signed exits are protected.
- V5 Correlated-failure and slashing exposure is bounded (client, cloud and region diversity).
- V6 Relay and builder trust is stated; reward accounting is verifiable.

## T: Exchange, settlement, payments, sweeping
- T1 Atomicity: both legs settle or neither; no exposure after a partial failure.
- T2 The internal ledger equals on-chain balances after every flow, failure paths included.
- T3 Deposit attribution cannot be spoofed or replayed (address derivation, memo or tag, reorgs, fake tokens, dust).
- T4 Sweeps and gas funding can only move funds to system-owned addresses.
- T5 Finality thresholds are defined per chain and applied before crediting.
- T6 Hot, warm and cold limits are enforced; replenishment needs higher approval than withdrawal.
- T7 Withdrawal pipeline: account takeover cannot bypass allow-list, delay and limit controls.
- T8 Proof of reserves and liabilities is complete, fresh and independently verifiable.
- T9 Screening and travel-rule checks cannot be bypassed or altered between check and release (the integrity of the control, not the compliance policy itself).

## G: Governance, operations, supply chain
- G1 Policy and configuration changes need a stronger quorum than what they govern, and are time-delayed and visible.
- G2 Audit logs are tamper-evident and outside the control of the actors they record.
- G3 Break-glass access is quorum-gated, alerted on and reviewed after use.
- G4 Build and deployment: reproducible or attested builds, signed artefacts, pinned dependencies; no single person can ship signing-path code.
- G5 Approver devices and UIs are independent, hardened and not built from one deployable artefact.
- G6 Monitoring detects invariant violations quickly enough to pause; pause authority is separate and tested.
- G7 Key-compromise and incident procedures exist, are rehearsed, and do not depend on the compromised path.
- G8 People: vetting at onboarding, least privilege, prompt offboarding, social-engineering resistance for privileged staff.
- G9 Third parties (custodians, RPC, oracle, cloud, auditors) have defined trust, failure handling and exit.
- G10 Web surface (DNS, frontend hosting, CDN, package registries) is protected against hijack and injection.
