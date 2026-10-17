# Misses log

How the skill gets better with use. Whenever something the review missed is found later (by a coverage audit, an architect, a pen test, an incident or a regulator), record it here. Then:

1. Add it to `golden-cases.md` as an expected finding, so future versions are tested against it.
2. If it is a pattern rather than a one-off, add a check to the relevant reference file (a completeness item, a lens check, a hunting technique or a recommendation pattern).
3. Re-run the golden cases, and note the skill version in the changelog below.

Record no confidential detail beyond what the team is cleared to keep here; describe the pattern, not the client.

## Log

| Date | Review | What was missed | Found by | Why it was missed (no check, check not applied, input gap, model error) | Fix made (golden case, checklist, lens, pattern) |
| --- | --- | --- | --- | --- | --- |
| 2026-10-17 | Skill self-review (no live review) | Chain-specific risks for Solana and other non-EVM chains: the blockchain lens was chain-neutral and leaned towards EVM | User | No check | New `references/chains.md` (universal questions plus ten chain profiles); Pass 1, Pass 5 gate and coverage audit require every chain in scope; Solana incidents added; golden case 5 |
| 2026-10-17 | Skill self-review against the original brief | No identity, API or data protection lens (recovery and help-desk paths, object-level authorisation, API keys, webhooks, KYC data, logs, deployment rights); coverage claimed rather than shown; no automatic independent pass | Gap analysis | No check | New `identity-api.md` and `data-protection.md` lenses; coverage ledger and workpapers (Template H); unshown paths added in Pass 2; six new hunting techniques; independent passes (section 2b) with specialist and auditor subagents; golden case 6 |

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-17 | First release: ten-pass procedure, six lenses, seven modes including coverage audit, external verification rule, HTML tools, Security Reviewer agent |
| 1.1 | 2026-10-17 | Chain profiles (Bitcoin, EVM and layer 2s, Solana, Cosmos, Aptos and Sui, XRPL, Stellar, Tron, TON, Polkadot) and universal questions for any other chain; Ed25519 derivation and threshold-scheme checks; Wormhole, Slope and `@solana/web3.js` incidents; golden case 5 (Solana) |
| 1.2 | 2026-10-17 | Identity, access and API lens; data protection lens; coverage ledger and workpapers; unshown paths; new hunting techniques; independent passes with Review Specialist and Coverage Auditor agents; Coinbase 2025 incident; golden case 6 |
| 1.3 | 2026-10-17 | Custody design principles DP-1 to DP-13, each with a sourced industry comparison and vendor questions; rule that principles decide findings and industry practice is comparison only; industry comparison line in recommendations; example recommendation |
