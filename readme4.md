Yes — but **you should sell Yoken to a LoB head very differently from how you sell it to the CISO**.

A CISO cares about enterprise cyber exposure. A CIB Payments, CCB, or AWM business leader cares about **running and scaling a product safely, avoiding disruption/loss, understanding dependencies, and not being surprised by something happening on a public network**.

That distinction should drive your pitch.

## The LoB problem Yoken solves

Imagine I'm the head of a business running a tokenised product on Base, Ethereum, Solana or another public chain.

I would ask you:

> **“Why do I need Yoken? My engineering and cybersecurity teams already monitor the product.”**

Your answer shouldn't begin with ontology, knowledge graphs, AI, AADAPT or graph analytics.

Start with:

> **“When you operate a regulated financial product on public blockchain infrastructure, part of your product's risk exists outside infrastructure the firm directly controls. Yoken gives you continuous visibility into whether changes in that external environment can affect your product, through which dependencies, what the potential business impact is, and whether action is required.”**

That is a business proposition.

And it is grounded in a real issue. The FSB specifically notes that when financial intermediaries use permissionless blockchains, there may be **no contractual third party responsible for managing the operational risks of the underlying infrastructure**, shifting risk-management responsibility toward the financial institution using it. ([Financial Stability Board][1])

The BIS/FSB also identify dependencies on custodians, oracles and bridges, along with smart-contract errors, private-key management, governance and interconnectedness, as potential vulnerabilities of tokenised systems. ([Bank for International Settlements][2])

That's almost the problem statement for Yoken.

---

# Don't sell them “security”. Sell them assurance.

The LoB proposition I'd use is:

> ### **Yoken provides continuous digital-asset product assurance.**
>
> **It tells the business whether developments across public blockchain infrastructure, protocols, dependencies and the threat landscape materially change the security or resilience of its products.**

That's much stronger than:

> “We've built an AI cyber-risk dashboard.”

The Bank of England itself is talking about moving tokenisation from pilots to production while preserving operational resilience, accountable governance and settlement finality. ([Bank of England][3])

So you're addressing a problem that becomes **more important as the business scales**, not less.

---

# Give the LoB head six things they don't have easily today

### 1. “Tell me whether my product is safe to operate.”

Their home screen starts with:

```text
JPMD
DIGITAL ASSET PRODUCT ASSURANCE

Operating posture             NORMAL

Security exposure             LOW
Blockchain dependency risk    LOW
Operational resilience        NORMAL
Material external threats     0
Active investigations         1
Control exceptions            0
```

And underneath:

> **No security condition currently identified that materially affects operation.**

That's useful to a business head.

---

### 2. “Tell me immediately when something outside the bank becomes relevant to me.”

This is probably your killer proposition.

Imagine a major exploit happens somewhere else.

The business doesn't need another alert saying:

> “New DeFi exploit — $150m lost.”

Yoken needs to say:

```text
NEW EXTERNAL SECURITY EVENT
           │
           ▼
Affected mechanism identified
           │
           ▼
Matching technology in our estate
           │
           ▼
Protocol A
           │
           ▼
JPMD

Potential exposure detected
Investigation initiated
```

Then tell the LoB:

> **A new attack has been observed externally. Yoken identified a potentially relevant dependency path to your product. Exposure is not yet confirmed. Security investigation YKN-147 is underway.**

That's actionable intelligence.

---

### 3. “Show me what my product actually depends upon.”

This is particularly important with public chains.

```text
                     JPMD
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
      Base         Custody         Contracts
        │
        ▼
     Ethereum
        │
   ┌────┼─────┐
   ▼    ▼     ▼
Sequencer RPC Infrastructure ...
```

Plus bridges, oracles, external protocols, wallets/signing infrastructure, off-chain services and other dependencies where applicable.

The LoB can ask:

> **“If X fails, what happens to my business?”**

Yoken traverses the graph and answers.

That is essentially **digital-asset dependency and concentration intelligence**.

This has broader regulatory relevance too: the Basel Committee's current third-party-risk principles emphasize critical-service dependencies and nth-party/supply-chain risk, while tokenisation introduces some dependency structures that don't map neatly onto traditional contractual third parties. ([Bank for International Settlements][4])

---

### 4. “Tell me what changed, not everything that happened.”

This is a huge usability differentiator.

The LoB dashboard every morning might say:

```text
WHAT CHANGED — LAST 24 HOURS

Public blockchain changes             2
Relevant security developments        3
New product exposures                 0
Dependency posture changes            1
Control changes                       0

──────────────────────────────────────

ONE ITEM REQUIRES ATTENTION

Bridge X
NORMAL → ELEVATED

Reason:
New attack technique observed against
comparable bridge architecture.

No confirmed impact to your product.
Investigation underway.
```

You're reducing an enormous global information space to:

> **What changed that matters to my business?**

---

### 5. “If something goes wrong, tell me what part of my business is affected.”

This is where the knowledge graph becomes extremely powerful.

Instead of:

> CVE-XXXX has CVSS 9.8.

Give the LoB:

```text
BUSINESS IMPACT

JPMD

Issuance                  UNAFFECTED
Redemption                UNAFFECTED
Settlement                UNAFFECTED
Protocol A integration    POTENTIALLY AFFECTED
Customer funds            NO EXPOSURE IDENTIFIED
Regulatory impact         UNDER ASSESSMENT
```

Then the architect can drill into the technical reasoning.

That's the connection traditional technical security reporting frequently struggles to make:

**Threat → technology → dependency → product → business capability → impact.**

---

### 6. “Tell me what decision you need from me.”

At the bottom:

```text
BUSINESS DECISIONS

No immediate action required
────────────────────────────────

UNDER INVESTIGATION

Protocol A exposure
Security owner: Digital Asset Security
Expected business impact: Medium

────────────────────────────────

UPCOMING

Base protocol upgrade
Architecture assessment complete
No material exposure identified
```

When there is a genuine issue:

```text
DECISION REQUIRED

Temporarily restrict Protocol A integration

Reason
Confirmed exposure to Attack X

Business capability affected
Secondary-market operation

Security recommendation
TEMPORARY RESTRICTION

[View Business Impact]
[View Technical Evidence]
```

Now Yoken is helping them **run the business**, rather than simply telling them about cyber threats.

---

# Different LoBs get different value

This is where Yoken becomes more interesting.

For **CIB Payments**, the important dimensions might be:

```text
Settlement availability
Finality
Transaction integrity
Key/signing compromise
Network/sequencer disruption
Liquidity dependencies
Cross-chain dependencies
Smart-contract integrity
Operational continuity
```

For **AWM**, perhaps:

```text
Tokenised fund integrity
NAV/oracle dependencies
Custody
Asset ownership
Issuance/redemption
Transfer restrictions
Smart contracts
Third-party protocols
Investor impact
```

For other banking businesses using public chains:

```text
Customer exposure
Payment continuity
Fraud
Wallet/key compromise
Transaction integrity
Chain dependencies
Consumer impact
Third-party dependencies
```

**Same Yoken graph and reasoning engine. Different business context.**

---

# The meeting pitch should be about 60 seconds

I would say something close to this:

> **“As we put more financial products onto public blockchain infrastructure, we inherit a new class of external dependencies. The blockchain, protocols, bridges, oracles and other infrastructure can change or come under attack independently of us.**
>
> **The problem Yoken addresses is simple: when something changes in that external environment, how quickly can we determine whether it matters to one of our products?**
>
> **Yoken continuously connects external security developments with our product architecture, dependencies and controls. Instead of telling you that another blockchain exploit happened, it tells you: does it affect your product, through what path, what business capability could be affected, how confident are we, and what decision—if any—is required?**
>
> **For the business, the outcome is continuous product assurance: what is our posture, what changed, what are we dependent upon, and is there anything we need to do?”**

Then stop talking.

Don't explain the ontology yet.

---

# Then demonstrate one scenario

This will convince them much more effectively than 30 architecture slides.

Start:

> **“Assume JPMD is operating normally.”**

Dashboard:

```text
JPMD                    NORMAL
```

Then:

> **“At 02:15, a new attack appears in the wild.”**

```text
External exploit
      ↓
Attack mechanism identified
      ↓
Yoken maps affected technology
      ↓
Dependency match
      ↓
Protocol A
      ↓
JPMD

POTENTIAL EXPOSURE
```

Then:

> **“Yoken launches an investigation.”**

```text
Attack prerequisites
       +
Our architecture
       +
Dependency state
       +
Controls
       +
Historical incidents
       ↓
PLAUSIBLE EXPOSURE
```

The LoB dashboard changes:

```text
JPMD

NORMAL
   ↓
ELEVATED

Issuance          Normal
Redemption        Normal
Settlement        Normal
Protocol A        Elevated

Action:
No suspension currently required.
Technical investigation underway.
```

Then show the CISO dashboard:

```text
NEW MATERIAL DIGITAL-ASSET EXPOSURE
JPMD — ELEVATED
```

Then show the architect dashboard with the complete graph and evidence.

That's the moment they understand **why you need three dashboards**.

---

And there's a broader tailwind to this proposition. UK authorities are explicitly trying to move tokenisation toward production: the Bank and FCA said in May 2026 that firms need confidence and clarity to scale tokenised wholesale markets, and the Bank describes the desired future as an interconnected multi-money, multi-asset, multi-currency ecosystem. ([Bank of England][3])

So I would frame Yoken internally as an **enabler**, not another control that makes public blockchain adoption harder:

> **“Security shouldn't just tell the business why public blockchains are risky. Yoken should give the business the assurance and evidence needed to use them safely.”**

That message is much more likely to resonate with a CIB/Payments/AWM LoB head than **“we've developed a sophisticated cyber threat knowledge graph.”**

[1]: https://www.fsb.org/uploads/P221024-2.pdf?utm_source=chatgpt.com "The Financial Stability Implications of Tokenisation"
[2]: https://www.bis.org/publications/fsi-summary-financial-stability-implications-tokenisation-executive-summary?utm_source=chatgpt.com "Financial stability implications of tokenisation - Executive Summary"
[3]: https://www.bankofengland.co.uk/news/2026/may/fca-and-boe-set-out-shared-vision-for-tokenisation-in-uk-wholesale-markets?utm_source=chatgpt.com "FCA and Bank of England set out shared vision for tokenisation in UK wholesale markets | Bank of England – the UK's central bank"
[4]: https://www.bis.org/publications/fsi-summary-sound-management-third-party-risk-executive-summary?utm_source=chatgpt.com "Sound management of third-party risk - Executive Summary"
