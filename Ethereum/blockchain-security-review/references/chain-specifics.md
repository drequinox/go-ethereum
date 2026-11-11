# Chain and platform specifics

Apply the list for each platform in scope during contract (pack C) and protocol (pack P) work. These are baseline prompts; refresh them in Phase 0B, because platform semantics change with upgrades.

## EVM chains
- Proxy patterns, storage-layout collisions, uninitialised implementations
- `delegatecall` targets and context
- `selfdestruct` semantics changed by EIP-6780 (Cancun); do not rely on old behaviour
- Transient storage (EIP-1153) and reentrancy guards built on it
- `CREATE2` redeployment at the same address
- Signature standards and their pitfalls: EIP-712, ERC-1271, EIP-2612 permit, ERC-4337 account abstraction, EIP-7702 delegation
- Opcode, precompile, gas and address-derivation differences across L2s and sidechains
- chainId handling across forks and replays

## Bitcoin and UTXO chains
- Script and Taproot spending paths; every path is a way to spend
- PSBT handling and change-address verification on the signing device
- Fee sniping, RBF, CPFP and transaction pinning
- Timelocks (absolute and relative) and their interaction with fees and reorgs
- Address reuse; descriptor and multisig backup completeness
- Lightning: channel state backups, watchtowers, force-close economics

## Solana
- Account ownership, signer and writable checks on every account
- PDA seed design and bump canonicalisation
- CPI privilege escalation and arbitrary program substitution
- Account reinitialisation, closing and revival
- Compute and rent limits

## Move chains (Aptos, Sui)
- Capability and resource handling; who can obtain a capability
- Object ownership and shared objects
- Generic type confusion
- Package upgrade policy
- Move Prover specifications where present

## Cosmos SDK, CometBFT, IBC
- Non-determinism in the state machine (maps, floats, time, goroutines)
- Module account permissions
- Ante handlers and fee logic
- IBC client trust, channel ordering and timeout handling
- Validator-set and light-client updates
- Vote extensions (ABCI++) where used

## Substrate and Polkadot
- Extrinsic weights and denial of service
- Runtime upgrade authority
- XCM origin checks and fee handling

## Enterprise platforms (Fabric, Corda, Canton, Besu/Quorum)
- See pack E. In addition: private-transaction manager behaviour, notary or ordering-service trust, endorsement and validation policy definitions, channel or privacy-group membership changes, chaincode lifecycle approvals.
