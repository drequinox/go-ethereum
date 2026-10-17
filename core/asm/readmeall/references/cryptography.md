# Cryptography lens

Apply to anything that generates, derives, stores, uses, backs up, rotates or destroys keys, and to any protocol that signs, encrypts or authenticates. Cite the evidence for each check; where the inputs are silent, ask.

Do not invent algorithm properties or standard requirements. If a point below does not apply to the system under review, skip it.

## Randomness and key generation

| Check | Why it matters | Evidence to ask for |
| --- | --- | --- |
| Keys and nonces come from a vetted CSPRNG or hardware RNG inside the security boundary | Weak or repeated randomness leaks keys | RNG source, DRBG construction, health tests |
| Virtual machines and containers that generate keys are never cloned or restored from snapshot while holding RNG state | Clones can repeat random output | Generation environment, snapshot policy |
| Keys are generated inside the HSM or MPC boundary and marked non-exportable (for PKCS#11: not extractable, sensitive) | A key that ever exists in application memory is exposed to that host | Key templates, generation calls |
| HSM validation level fits the asset; FIPS 140-2 certificates moved to the historical list in September 2026, so new deployments should require FIPS 140-3 | Validation scope and currency matter in audits | Certificate number, level, scope, firmware version |
| Seeds and mnemonics, if used, are generated in the boundary and never displayed on a networked device | Any display or transcription is an extraction path | Ceremony script |

## Signature schemes

| Check | Why it matters |
| --- | --- |
| ECDSA nonces are unique, secret and unbiased: deterministic per RFC 6979 or generated in hardware | Reused or biased nonces reveal the private key |
| Signatures are normalised where the chain requires it (for example low-s on Ethereum and Bitcoin) | Malleable signatures can break transaction tracking and idempotency |
| EdDSA and Schnorr implementations are vetted and take the public key from the key itself, not from caller input | Some libraries leaked keys when given a mismatched public key |
| Schnorr and multi-party Schnorr (for example MuSig2) never reuse a nonce across sessions, including after a crash or retry | Nonce reuse in multi-round protocols reveals keys |
| Public keys and points are validated (on curve, correct subgroup) | Invalid-curve inputs can leak secrets |
| Vetted libraries only (for example libsecp256k1); no in-house primitives | Custom cryptography is the most common source of critical bugs |

## Threshold signing and MPC

| Check | Why it matters |
| --- | --- |
| Protocol choice is named, with its security model (malicious vs honest-but-curious parties) | Many deployed protocols assume honest participants |
| Implementations of older protocols (GG18, GG20, Lindell17) include the zero-knowledge proofs later shown to be missing in several products (BitForge, TSSHOCK, 2023) | Missing proofs let one malicious party extract the full key |
| Preference for protocols with identifiable abort and current proofs (for example CGGMP21), in an independently audited implementation | Abort handling and proofs are where attacks live |
| Shares are held by genuinely independent parties: different operators, infrastructure, clouds or HSMs | Shares in one environment are one key with extra steps |
| Shares are refreshed proactively and on any change of operator or suspected compromise | Refresh limits the value of slowly stolen shares |
| Failed or aborted signing sessions are treated as security events and never retried with the same nonce material | Repeated aborts can be an extraction attack |
| Presignatures, if used, are stored and consumed safely and bound to the intended message | Misused presignatures enable forgeries |
| Share backups are encrypted to keys held under separate custody, and restore is tested | Backups often become the weakest copy |

## Derivation (HD wallets)

| Check | Why it matters |
| --- | --- |
| Account-level paths use hardened derivation | With non-hardened derivation, an extended public key plus any one child private key reveals the parent private key |
| Extended public keys are treated as sensitive whenever any non-hardened child key could leak | Exposure of the xpub turns one leak into total loss, and also reveals all addresses |
| Derivation paths are assigned by the system, not chosen by callers, and collisions are prevented | Caller-chosen paths can collide or reach keys of another client |
| Mapping from client or account to path is recorded and audited | Needed for recovery and for proving ownership |

## Binding and domain separation

| Check | Why it matters |
| --- | --- |
| Signing endpoints sign structured, typed payloads that the policy engine can parse | Raw-hash signing lets anyone with access sign arbitrary transactions blindly |
| Raw or arbitrary-message signing is disabled or tightly governed | It bypasses amount, destination and contract checks |
| Signatures are bound to chain and context (chain ID, EIP-712 domain, protocol tags) | Prevents replay across chains, contracts or message types |
| One key is not used for unrelated purposes (transaction signing and authentication, for example) | Cross-protocol attacks become possible |

## Encryption, backups and key hierarchy

| Check | Why it matters |
| --- | --- |
| Authenticated encryption (for example AES-GCM, ChaCha20-Poly1305) with unique nonces | Nonce reuse in GCM breaks confidentiality and integrity |
| A key hierarchy (key-encryption keys over data keys) with defined rotation and lifecycle states, following NIST SP 800-57 practice | Rotation and compromise handling depend on it |
| Backup key-encryption keys are split M of N (for example on smartcards) held by independent custodians | One custodian must not be able to restore |
| Where secrets are reassembled (Shamir), the reconstruction point is itself protected and audited; verifiable secret sharing detects bad shares | Reconstruction recreates a single point of failure |
| Restore is tested on a schedule, end to end, into an isolated environment | Untested backups fail when needed |

## Authentication cryptography

| Check | Why it matters |
| --- | --- |
| Approvers and signers use phishing-resistant authenticators (WebAuthn or passkeys, smartcards) with user verification required | Passwords and OTP are phishable |
| For staff approvers, device-bound credentials with attestation, rather than passkeys synced through consumer accounts | A synced passkey is only as strong as the cloud account recovery behind it |
| Relying party and origin settings are scoped correctly | Mis-scoped origins allow cross-site credential use |
| Service identities use mutual TLS or signed tokens with short lifetimes and pinned trust for signer channels | Long-lived static secrets leak |

## Agility and post-quantum

| Check | Why it matters |
| --- | --- |
| An inventory of where the firm controls the algorithm (transport, backups, internal signing, authentication) versus where the blockchain fixes it | Only the former can be migrated by the firm |
| Long-lived confidential data, including encrypted key share backups and share transport, is assessed for harvest-now-decrypt-later risk | Data captured today may be decrypted later |
| A migration path to NIST's post-quantum standards (FIPS 203, 204, 205, published 2024) where the firm controls the algorithm | Regulators increasingly ask for transition plans |
| Trusted execution environments are treated as defence in depth, not as the only boundary | TEEs have a history of side-channel breaks |
