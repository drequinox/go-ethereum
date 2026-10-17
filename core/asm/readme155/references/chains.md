# Chain profiles

Apply with the blockchain lens. In Pass 1, list **every chain and token standard in scope**, including chains that are only planned. For each one, apply the universal questions below, then that chain's profile. Chain behaviour differs fundamentally: never carry one chain's assumptions to another. The loss paths that matter most are often specific to a chain.

Facts below were checked against the linked official sources on 17 October 2026. Chains change through upgrades: re-verify any chain fact that a High or Critical finding depends on (external verification rule in SKILL.md).

## Universal questions (apply to every chain, including chains not profiled here)

If a chain in scope has no profile below, answer these from its **official documentation**. Cite each answer, and state in the review: "Chain not profiled in the skill; checked against <source>". If there is no web access, list the questions in the verification plan instead.

| # | Question | Why it matters |
| --- | --- | --- |
| U1 | **Authority model.** What controls an address or account? Can control change *without the address changing* (key rotation, permission update, authority reassignment, owner change, code delegation)? | These operations hand over an account silently. Treat every one as at least as sensitive as a full-balance withdrawal |
| U2 | **Delegated powers.** What approvals, grants, proxies, delegates, session keys or allowances exist, and do they expire? | Standing delegations are backdoors that need no further signature |
| U3 | **What is signed.** Can one transaction carry several instructions or messages? Does the policy engine decode and check *all* of them, with addresses fully resolved? | Policy that checks only the first transfer misses the rest |
| U4 | **Replay and expiry.** What binds a signature to this chain and network (chain ID, genesis hash, network passphrase)? When does a signed transaction expire, if ever? | A signed but unbroadcast transaction that never expires is a bearer instrument |
| U5 | **Finality.** What finality model does the chain have, what status does the RPC report, and are consensus changes scheduled? | Crediting before finality enables double spends; consensus upgrades change the meaning of statuses |
| U6 | **Deposit semantics.** Are memos or tags required? How do you get the amount *actually delivered*? How is a token identified (contract, mint, denom, issuer, master)? | Fake tokens, partial deliveries and missing tags are classic exchange losses |
| U7 | **Issuer powers.** Can the token issuer freeze, claw back, burn from, or move tokens in holders' accounts? | Balances in custody can change without any custody signature |
| U8 | **Account lifecycle.** Reserves, rent, existential deposits, account deletion or reaping, activation requirements | Accounts can disappear or fail to receive |
| U9 | **Code mutability.** Who can upgrade the contracts or programs the custody path calls, with what delay? | The upgrade authority is a master key over every user of that code |
| U10 | **Keys.** Curve, signature scheme, derivation standard, and whether the MPC or HSM supports it natively | Unsupported schemes push keys into application memory |
| U11 | **Fees.** Who pays, can fees be sponsored, and are there fee ceilings? | Sponsored-fee and fee-limit logic is drainable |
| U12 | **Staking authorities.** Which keys control staking, unstaking and withdrawal of staked principal? | Operator keys must not control principal |

---

## Bitcoin and UTXO chains

| Check | Why it matters |
| --- | --- |
| Transactions are built and passed as PSBTs (BIP-174, BIP-370), and the signer independently verifies every output, including that change outputs pay back to the wallet's own descriptor | A substituted change address is a silent theft |
| The signer verifies input amounts (the fee is inputs minus outputs). Taproot (BIP-341) signatures commit to all input amounts and scripts; for SegWit v0 inputs, the signer must check the previous transactions | Lying about input amounts to an offline signer can burn funds as fees or steal them |
| Unconfirmed transactions are treated as replaceable: full replace-by-fee has been the Bitcoin Core default since version 28.0 | Zero-confirmation crediting is unsafe |
| Fee bumping (RBF, CPFP) is governed like a new transaction, with fee ceilings | Replacement can redirect outputs |
| Wallets are described by output descriptors and script policies (for example miniscript) that are reviewed and backed up with the keys | Without the descriptor, keys alone may not recover multisig or Taproot funds |
| Confirmation depth for crediting is set per asset and amount; deposits are watched for reorgs | Reorgs reverse unconfirmed history |

## Ethereum and EVM chains, including layer 2s

| Check | Why it matters |
| --- | --- |
| Chain ID binding (EIP-155) and typed-data domains (EIP-712) are checked on every signature | Prevents cross-chain and cross-contract replay |
| **EIP-7702** (live on mainnet since the Pectra upgrade, 7 May 2025): custody keys never sign authorizations, and the signer blocks them by default. An authorization with chain ID 0 is valid on every chain | One authorization can set code on the EOA that drains it with no further signature. The EIP itself says there is no safe way for wallets to expose this to applications |
| Approvals, permit and permit2 signatures, and setApprovalForAll are bounded, monitored and revocable | Signed approvals are the most common theft route that needs no transaction from the victim |
| Each L2's trust model is recorded: sequencer control, forced inclusion, proof system, upgrade keys and the withdrawal delay to L1 (for example the challenge period of optimistic rollups) | L2 security and liquidity are not those of L1 |
| The same address on different EVM chains is not assumed to be controlled by the same party for contract wallets | Contract wallets deployed on one chain may not exist, or may belong to someone else, on another |
| Nonce management, fee ceilings (EIP-1559 maximum fee), multisig and delegatecall controls are covered in the blockchain lens | |

## Solana

| Check | Why it matters |
| --- | --- |
| **Every instruction in a transaction is decoded and checked by policy.** Versioned (v0) transactions resolve accounts through address lookup tables, so policy resolves them on the signer side and checks the resolved addresses. Lookup tables used in custody transactions are controlled by a custody-governed authority, or frozen | Drainers hide a harmful instruction among benign ones; unresolved lookup-table entries hide destinations; whoever controls a lookup table can extend it |
| **Authority-changing instructions are blocked or need elevated approval:** token account owner changes (SetAuthority), System Program Assign, stake and nonce Authorize, program upgrade authority changes, and token Approve (delegate) | A token account's owner can be changed without moving any tokens; the attacker withdraws later. Token-2022 associated token accounts have an immutable owner by default; original SPL Token accounts do not |
| **Durable nonces.** A transaction using a durable nonce does not expire (normal transactions expire after a 150-slot recent-blockhash window). Signed durable-nonce transactions are stored as sensitive, and the nonce authority is a custody key. To cancel one, advance the nonce | A signed, unbroadcast durable-nonce transaction stays valid until the nonce advances |
| **Commitment.** Credit deposits only at "finalized" commitment. The Alpenglow consensus upgrade changes the semantics: under Alpenglow, confirmed and finalized become equivalent. solana.com gives an estimated mainnet activation of 21 October 2026. Re-check crediting logic, and RPC provider support, against the live consensus | Crediting at "processed" or "confirmed" today risks rollback; logic written for TowerBFT may be wrong after Alpenglow |
| **Token identity.** Deposits are credited by mint address and token program (SPL Token or Token-2022), never by name or symbol | Fake mints with real names are common |
| **Token-2022 extensions are reviewed per mint before an asset is supported:** permanent delegate (the issuer can move or burn tokens in any account), transfer hook (issuer code runs on every transfer), transfer fee (the recipient receives less), default frozen state, confidential transfers, memo-required, and mint close authority (a closed mint can be reinitialised at the same address with different extensions) | Each can change balances, block withdrawals or break reconciliation without a custody signature |
| **Program upgrades.** For every program the custody path calls, record the upgrade authority, or confirm it is immutable (`--final`). Treat an upgradeable program as code its upgrade authority can change at will | The upgrade authority can replace the program's logic |
| **Program audits** include signer, owner and account-validation checks, and verification of sysvar accounts | The Wormhole loss came from an unverified sysvar account (see incidents) |
| **Stake accounts.** The withdraw authority is held under custody; the stake authority may be an operator key. The withdraw authority can reset the stake authority | The withdraw authority controls the principal |
| **Fee payer and priority fees.** When the firm pays fees for transactions built by others, it signs only fully decoded transactions that pass policy, with ceilings on priority fees and compute | A sponsored fee payer is a signing oracle |
| **Simulation.** Results are advisory: state can change between simulation and execution. Policy checks the instructions themselves, not only simulated balance changes | Drainers exploit differences between simulation and execution |
| **Keys.** Solana uses Ed25519. HD derivation follows SLIP-0010 (hardened only); threshold signing needs an EdDSA protocol such as FROST (RFC 9591), not an ECDSA protocol | Mismatched derivation loses funds; an unsupported curve pushes keys into application memory |
| **Client libraries are pinned and verified.** `@solana/web3.js` 1.95.6 and 1.95.7 were malicious (CVE-2024-54134) | Server-side signers that hold raw keys are the target of supply-chain attacks |

## Cosmos SDK chains

| Check | Why it matters |
| --- | --- |
| Sign documents bind chain ID, account number and sequence; these are checked per chain | Prevents cross-chain replay among Cosmos chains |
| **authz grants are blocked or governed.** A GenericAuthorization gives unrestricted execution of one message type on the granter's behalf, and a grant without an expiry never expires. feegrant allowances are bounded | A grant is a standing delegation that can move funds through MsgExec |
| IBC tokens are identified by full denom trace (`ibc/<hash>` resolved to channel and base denom), never by display name | The same display name can arrive over different channels from different issuers |
| Deposit memos are required and enforced for shared deposit addresses | Missing memos leave funds unattributed |
| Each chain's own upgrade governance and validator set are considered | Every Cosmos chain is sovereign; security differs per chain |

## Move chains (Aptos, Sui)

| Check | Why it matters |
| --- | --- |
| **Aptos:** the authentication key can be rotated while the address stays the same. Custody monitors rotation events, and the signer blocks rotation unless it is under a governed ceremony | Rotation hands over an account without changing its address, and the current key cannot be derived from the address |
| **Aptos:** where unproven rotations are possible, the address-to-key mapping is tracked by the firm | The on-chain reverse mapping is not updated for unproven rotations |
| **Sui:** sponsored transactions are signed by the gas owner only after full decoding and policy checks | The sponsor is otherwise a signing oracle |
| Package upgrades: record who holds the upgrade capability and the upgrade policy, for every package the custody path calls | Upgradeable packages can change behaviour |
| Token identity is checked by full type or object identifier, not display metadata | Look-alike coins are easy to create |

## XRP Ledger

| Check | Why it matters |
| --- | --- |
| **Incoming payments are credited from the `delivered_amount` metadata field, never from `Amount`** | With the partial-payment flag, a sender can set a large Amount and deliver almost nothing. This is the documented partial payments exploit |
| Destination tags are required and enforced (RequireDest) on shared accounts | Missing tags leave deposits unattributed |
| **Authorisation methods are inventoried.** Master key, regular key (SetRegularKey) and signer list (SignerListSet) can all be enabled together. If multisigning is the control, disable the master key and remove the regular key; changes to any of them need elevated approval | A signer list does not stop an enabled master or regular key from signing alone |
| Trust lines and issuer settings, including freeze and clawback, are reviewed for each issued asset | Issued assets carry issuer powers |
| Account reserves and LastLedgerSequence (transaction expiry) are handled | Unhandled reserves block sends; missing expiry leaves transactions pending indefinitely |

## Stellar

| Check | Why it matters |
| --- | --- |
| Signers, weights and thresholds (set via SetOptions) are inventoried, and changes need elevated approval | Adding a signer hands over the account |
| Asset issuers' authorisation and clawback flags are reviewed per asset | Clawback-enabled assets can be removed from custody accounts by the issuer |
| Memos are required for shared deposit accounts, and the network passphrase is checked | Unattributed deposits; cross-network replay |

## Tron

| Check | Why it matters |
| --- | --- |
| **AccountPermissionUpdate is blocked or needs the highest approval.** Owner and active permissions (keys, weights, thresholds) are monitored for change | Attackers who obtain a key add their own address or replace the owner permission. The victim can still receive but no longer send, and the attacker drains later |
| TRC-20 tokens are identified by contract address | Fake USDT contracts are common |
| Energy and bandwidth and fee limits are set, with ceilings | Fee exhaustion stalls withdrawals |

## TON

| Check | Why it matters |
| --- | --- |
| **Jetton deposits are verified as the TON documentation prescribes:** allow-list the jetton master, derive the expected jetton wallet with `get_wallet_address`, check that the sender is that wallet, check the opcode is `transfer_notification`, then parse amounts in base units | Fake jetton wallets with inflated balances are credited otherwise |
| Asynchronous message chains and bounces are handled: credit only on final notification; refund paths are tested | A transfer is several messages; partial completion is possible |
| Wallet contract versions are recorded | Versions differ in features and security properties |

## Substrate and Polkadot

| Check | Why it matters |
| --- | --- |
| **Proxies are inventoried.** No "Any" proxies on custody accounts (they allow balance transfers); prefer restricted types with a time delay, so controlling accounts can cancel within the window | A proxy is standing delegated control |
| Existential deposit and account reaping are handled | Accounts below the minimum are removed |
| Transactions use mortal eras (an expiry) where possible, and genesis hash binding is checked | Bounded validity; no cross-chain replay |

---

## Sources

| Chain | Sources |
| --- | --- |
| Bitcoin | [BIP-341 sighash discussion](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2020-May/017808.html), [Bitcoin Core 28.0 release notes](https://bitcoincore.org/en/releases/28.0/), [BIPs](https://github.com/bitcoin/bips) |
| Ethereum | [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702), [Pectra mainnet activation](https://ethpandaops.io/posts/pectra-mainnet-checklist/) |
| Solana | [Durable nonces](https://solana.com/docs/core/transactions/durable-nonces), [Commitment status (Anza)](https://docs.anza.xyz/consensus/commitments), [Alpenglow status](https://solana.com/upgrades/alpenglow), [Immutable owner](https://solana.com/developers/guides/token-extensions/immutable-owner), [Stake accounts](https://solana.com/docs/references/staking/stake-accounts), [Deploying programs](https://solana.com/docs/programs/deploying), [Token-2022 security (Neodyme)](https://neodyme.io/de/blog/token-2022), [CVE-2024-54134](https://advisories.gitlab.com/npm/@solana/web3.js/CVE-2024-54134/) |
| Cosmos | [authz module](https://docs.cosmos.network/sdk/next/modules/authz/README.md) |
| Aptos, Sui | [Aptos key rotation](https://aptos.dev/build/guides/key-rotation), [Sui sponsored transactions](https://docs.sui.io/learn/sponsored-transactions), [Sui package upgrades](https://docs.sui.io/build/package-upgrades) |
| XRP Ledger | [Partial payments](https://xrpl.org/docs/concepts/payment-types/partial-payments/), [Multi-signing](https://xrpl.org/docs/concepts/accounts/multi-signing.md) |
| Stellar | [Clawbacks](https://developers.stellar.org/docs/build/guides/transactions/clawbacks) |
| Tron | [AccountPermissionUpdate](https://docs.chainstack.com/reference/tron-accountpermissionupdate.md), [imToken security alert on permission scams](https://support.token.im/hc/en-us/articles/12718931255193-Security-Alert-Beware-of-TRX-Multisig-Scams) |
| TON | [Jetton payment processing](https://docs.ton.org/payments/jettons) |
| Polkadot | [Proxies](https://wiki.polkadot.com/learn/learn-proxies/) |
