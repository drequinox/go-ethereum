# Incident lessons

Real losses show where adversaries actually go. Use these to prioritise attack paths and to justify recommendations. Figures are approximate and as publicly reported; check primary sources before quoting them in a deliverable.

| Incident | What happened (public reporting) | Lesson | Check to apply |
| --- | --- | --- | --- |
| Bybit, February 2025, about USD 1.5 billion | A developer machine at the multisig wallet provider (Safe{Wallet}) was compromised and malicious code was served in the wallet interface used by Bybit's signers. Signers approved a transaction that replaced the wallet's implementation through delegatecall. Attributed to North Korean actors. | A quorum is defeated if every signer trusts the same interface | Independent transaction decoding on a separate path; block or escalate delegatecall and implementation changes; integrity of front-end code served to signers |
| WazirX, July 2024, about USD 230 million | Signers of a multisig wallet approved a transaction whose displayed details differed from the actual payload, enabling a contract upgrade | What approvers see must be bound to what they sign | Display integrity; simulation before signing; time delay on upgrades |
| Radiant Capital, October 2024, about USD 50 million | Malware delivered through a message impersonating a former contractor infected several signers' devices; the interface showed legitimate transactions while malicious ones were signed | Signer devices are part of the custody boundary | Dedicated signing devices; hardware wallet display checks; device diversity across approvers |
| DMM Bitcoin, May 2024, about USD 300 million | Attributed by US and Japanese authorities to North Korean actors who socially engineered an employee of the firm's wallet software vendor and manipulated a legitimate transaction request | Vendor staff are part of the attack surface | Vendor trust model; vendor access scope; independent verification of requests that pass through a vendor |
| Ronin bridge, March 2022, about USD 600 million | Attackers obtained five of nine validator keys: four from one operator, one through a delegated arrangement that had not been revoked. Entry reportedly via a fake job offer. The theft went unnoticed for days. | Threshold without independence is not a threshold; stale delegations persist; detection matters | Quorum independence; review of delegations; alerting on signing outside the expected path |
| Harmony Horizon bridge, June 2022, about USD 100 million | A 2-of-5 multisig was defeated by compromising two keys | Low thresholds fail | Threshold such that threshold-minus-one compromises cannot sign |
| Ledger Connect Kit, December 2023 | A widely used front-end library was published with wallet-draining code after a former employee was phished | Third-party front-end code can turn every user into a victim within hours | Pinned and verified dependencies; subresource integrity; release signing |
| BitForge and TSSHOCK disclosures, 2023 | Researchers showed that several implementations of common threshold ECDSA protocols lacked proofs that stop a malicious party from extracting the key | MPC security depends on the implementation, not the label | Name the protocol and implementation; require evidence of fixes and independent audit |

## Patterns across these incidents

1. **The interface is the target.** Attackers compromise what signers see, not the keys themselves.
2. **People and vendors are the entry point.** Fake recruiters, fake contractors and vendor staff appear repeatedly.
3. **Common-mode failure beats thresholds.** Many approvers on the same software, devices or vendor count as one.
4. **Upgrade and delegatecall paths hand over everything.** One signature on the wrong call type is total loss.
5. **Detection is slow.** Several losses were noticed hours or days later.
