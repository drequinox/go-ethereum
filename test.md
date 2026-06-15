I verified the overall architecture. It is correct, but I would not honestly call any ontology process “100% foolproof.” Elite ontologists reduce error by using standards reuse, competency questions, controlled vocabularies, validation constraints, evidence/provenance, test cases, and versioning. STIX is the CTI exchange/object model; ATT&CK is the general adversary-behaviour taxonomy; AADAPT is the digital-asset-specific adversary-behaviour taxonomy; SHACL is the validation layer if you represent the ontology/graph in RDF. STIX is explicitly for exchanging CTI and representing suspicion, compromise, attribution, objects, and relationships; ATT&CK is a real-world adversary tactics/techniques knowledge base; MITRE’s ATT&CK STIX repository provides ATT&CK in STIX 2.1 JSON; AADAPT is MITRE’s complementary digital-asset payment technology adversary framework; and SHACL is the W3C constraint language for validating RDF graphs.  

Elite step-by-step method

Step 1: Do not start with the LLM

Start with the purpose:

Build a reusable Digital Asset Threat Intelligence Ontology for DeFi, blockchain security, custody, wallet, tokenized asset, and digital payment incidents, so that new incidents are mapped into a stable schema rather than generating a new ontology every time.

The LLM is allowed to help draft, but it must never be allowed to freely invent the ontology.

⸻

Step 2: Define the four-layer architecture

Your reusable ontology should have four stable layers:

Layer 1: CTI Core
Source, Report, Evidence, Incident, ThreatActor, Campaign, Indicator, Malware, Tool, Vulnerability, Weakness, ObservedData
Layer 2: Adversary Behaviour
ATTACKTactic, ATTACKTechnique, ATTACKSubTechnique, AADAPTTactic, AADAPTTechnique, AADAPTSubTechnique, Procedure
Layer 3: Digital Asset Infrastructure
Blockchain, Layer1, Layer2, Protocol, DeFiProtocol, Bridge, SmartContract, TokenContract, Wallet, Address, Custodian, Oracle, Sequencer, Validator, RPCProvider, Indexer, Exchange, Issuer
Layer 4: Asset and Risk
DigitalAsset, DepositToken, Stablecoin, TokenizedMMF, TokenizedSecurity, RWA, Control, RiskAssessment, RiskFactor, Likelihood, Impact, Exposure, Confidence

This structure is correct because it separates:

Evidence → behaviour → infrastructure → business risk

That is what makes it reusable.

⸻

Step 3: Decide where each standard fits

Use STIX for CTI objects and evidence/provenance:

Report
ThreatActor
Campaign
Indicator
Malware
Tool
Vulnerability
Relationship
Sighting
ObservedData
CourseOfAction

Use ATT&CK for general cyber adversary behaviour:

Phishing
Valid Accounts
Credential Theft
Command and Scripting Interpreter
Exfiltration
Impact

Use AADAPT for digital-asset-specific adversary behaviour:

Siphon Funds
Generate Counterfeit Tokens
Exploit External Services
Intercept API Communication
Side-Channel Attack
other digital asset payment technology techniques

AADAPT has official technique pages such as ADT3028 Siphon Funds, ADT3016 Generate Counterfeit Tokens, ADT3008 Exploit External Services, and ADT3018 Intercept API Communication, which confirms it should be modelled as a controlled technique taxonomy, not as free-form LLM labels.  

Use CVE/CWE/CISA KEV for vulnerability grounding:

CVE = vulnerability identifier
CWE = weakness category
CISA KEV = known exploited in the wild

CISA KEV is specifically a catalog for known exploited vulnerabilities and includes fields such as CVE, vendor/project, product, date added, action, and CWE notes.  

⸻

Step 4: Define classes, not incident names

Classes should be reusable:

SmartContract
Bridge
Wallet
AADAPTTechnique
RiskAssessment

Do not create classes like:

EulerHack
CurveExploit
LazarusBridgeIncident
JPMDPhishingCase

Those are instances.

Correct:

Euler exploit = Incident instance
Curve pool = Protocol/LiquidityPool instance
Lazarus = ThreatActor instance
JPMD = DepositToken instance
Base = Layer2 instance

This is one of the most important ontology rules.

⸻

Step 5: Define canonical relationships

Use a strict relationship catalogue.

Source PUBLISHED Report
Report CONTAINS Evidence
Evidence SUPPORTS Relationship
Report DESCRIBES Incident
ThreatActor CONDUCTS Campaign
Campaign INVOLVES Incident
Incident USES ATTACKTechnique
Incident USES AADAPTTechnique
Incident TARGETS DigitalAsset
Incident EXPLOITS Vulnerability
DigitalAsset DEPLOYED_ON Blockchain
DigitalAsset ISSUED_BY Issuer
DigitalAsset CUSTODIED_BY Custodian
DigitalAsset DEPENDS_ON Protocol
DigitalAsset DEPENDS_ON SmartContract
DigitalAsset DEPENDS_ON Oracle
DigitalAsset DEPENDS_ON Sequencer
Protocol RUNS_ON Blockchain
SmartContract BELONGS_TO Protocol
TokenContract REPRESENTS DigitalAsset
Wallet CONTROLS Address
Address INTERACTS_WITH SmartContract
Address FUNDED Address
Control MITIGATES ATTACKTechnique
Control MITIGATES AADAPTTechnique
Control REDUCES RiskFactor
RiskAssessment ASSESSES DigitalAsset
RiskFactor CONTRIBUTES_TO RiskAssessment

This relationship catalogue is the real backbone of the knowledge graph.

⸻

Step 6: Write competency questions first

Elite ontology work starts with questions the ontology must answer. Competency questions are widely used to guide ontology scope and validation.  

Use these:

Which incidents target JPMD on Base?
Which incidents target tokenized MMFs on Solana?
Which AADAPT techniques appear in DeFi bridge exploits?
Which ATT&CK techniques commonly precede wallet compromise?
Which assets depend on a specific bridge, oracle, custodian, sequencer, or smart contract?
Which controls mitigate the techniques used in a given incident?
Which vulnerabilities affect smart contracts or external services?
Which incidents share wallets, indicators, contracts, techniques, or threat actors?
Which evidence supports a specific relationship?
What risk factors contribute to the current risk score for a named asset?

If a class or relationship does not help answer these questions, do not add it.

⸻

Step 7: Create the ontology JSON file

Create:

mkdir -p ontology
nano ontology/digital_asset_ti_v1.json

Use this skeleton:

{
  "ontology_name": "Digital Asset Threat Intelligence Ontology",
  "version": "1.0",
  "status": "stable",
  "purpose": "Reusable ontology for DeFi, blockchain security, custody, wallet, payment technology, tokenized asset, and digital asset threat intelligence.",
  "standards_alignment": {
    "stix_2_1": "CTI object model, reports, indicators, observed data, relationships, sightings, and provenance.",
    "mitre_attack": "General adversary tactics, techniques, procedures, mitigations, groups, campaigns, and software.",
    "mitre_aadapt": "Digital asset payment technology adversary tactics and techniques.",
    "cve_cwe_cisa_kev": "Vulnerability identifiers, weakness classes, and known exploited vulnerability evidence."
  },
  "entity_types": {
    "cti_core": [
      "Source",
      "Report",
      "Evidence",
      "Incident",
      "Campaign",
      "ThreatActor",
      "Indicator",
      "ObservedData",
      "Malware",
      "Tool",
      "Vulnerability",
      "Weakness",
      "CourseOfAction",
      "Identity"
    ],
    "behaviour": [
      "Tactic",
      "Technique",
      "SubTechnique",
      "Procedure",
      "ATTACKTactic",
      "ATTACKTechnique",
      "ATTACKSubTechnique",
      "AADAPTTactic",
      "AADAPTTechnique",
      "AADAPTSubTechnique"
    ],
    "digital_asset_infrastructure": [
      "Blockchain",
      "Layer1",
      "Layer2",
      "Protocol",
      "DeFiProtocol",
      "Bridge",
      "SmartContract",
      "TokenContract",
      "Wallet",
      "Address",
      "Custodian",
      "KeyManagementSystem",
      "MPCService",
      "HSM",
      "Oracle",
      "Sequencer",
      "Validator",
      "RPCProvider",
      "Indexer",
      "Exchange",
      "Issuer",
      "TransferAgent",
      "LiquidityPool",
      "Governance"
    ],
    "asset_and_risk": [
      "DigitalAsset",
      "DepositToken",
      "Stablecoin",
      "TokenizedMMF",
      "TokenizedSecurity",
      "RWA",
      "TreasuryAsset",
      "Control",
      "RiskAssessment",
      "RiskFactor",
      "Likelihood",
      "Impact",
      "Exposure",
      "Confidence"
    ]
  }
}

⸻

Step 8: Add relationship rules

Add:

{
  "relationships": [
    {"source": "Source", "relation": "PUBLISHED", "target": "Report"},
    {"source": "Report", "relation": "CONTAINS", "target": "Evidence"},
    {"source": "Evidence", "relation": "SUPPORTS", "target": "Incident"},
    {"source": "Evidence", "relation": "SUPPORTS", "target": "RiskFactor"},
    {"source": "ThreatActor", "relation": "CONDUCTS", "target": "Campaign"},
    {"source": "Campaign", "relation": "INVOLVES", "target": "Incident"},
    {"source": "Incident", "relation": "USES", "target": "ATTACKTechnique"},
    {"source": "Incident", "relation": "USES", "target": "AADAPTTechnique"},
    {"source": "Incident", "relation": "TARGETS", "target": "DigitalAsset"},
    {"source": "Incident", "relation": "EXPLOITS", "target": "Vulnerability"},
    {"source": "Vulnerability", "relation": "HAS_WEAKNESS", "target": "Weakness"},
    {"source": "Vulnerability", "relation": "AFFECTS", "target": "SmartContract"},
    {"source": "Vulnerability", "relation": "AFFECTS", "target": "Protocol"},
    {"source": "DigitalAsset", "relation": "DEPLOYED_ON", "target": "Blockchain"},
    {"source": "DigitalAsset", "relation": "ISSUED_BY", "target": "Issuer"},
    {"source": "DigitalAsset", "relation": "CUSTODIED_BY", "target": "Custodian"},
    {"source": "DigitalAsset", "relation": "DEPENDS_ON", "target": "Protocol"},
    {"source": "DigitalAsset", "relation": "DEPENDS_ON", "target": "SmartContract"},
    {"source": "DigitalAsset", "relation": "DEPENDS_ON", "target": "Oracle"},
    {"source": "DigitalAsset", "relation": "DEPENDS_ON", "target": "Sequencer"},
    {"source": "DigitalAsset", "relation": "DEPENDS_ON", "target": "Bridge"},
    {"source": "Protocol", "relation": "RUNS_ON", "target": "Blockchain"},
    {"source": "SmartContract", "relation": "BELONGS_TO", "target": "Protocol"},
    {"source": "TokenContract", "relation": "REPRESENTS", "target": "DigitalAsset"},
    {"source": "Wallet", "relation": "CONTROLS", "target": "Address"},
    {"source": "Address", "relation": "INTERACTS_WITH", "target": "SmartContract"},
    {"source": "Address", "relation": "FUNDED", "target": "Address"},
    {"source": "Control", "relation": "MITIGATES", "target": "ATTACKTechnique"},
    {"source": "Control", "relation": "MITIGATES", "target": "AADAPTTechnique"},
    {"source": "Control", "relation": "REDUCES", "target": "RiskFactor"},
    {"source": "RiskAssessment", "relation": "ASSESSES", "target": "DigitalAsset"},
    {"source": "RiskFactor", "relation": "CONTRIBUTES_TO", "target": "RiskAssessment"},
    {"source": "RiskAssessment", "relation": "HAS_LIKELIHOOD", "target": "Likelihood"},
    {"source": "RiskAssessment", "relation": "HAS_IMPACT", "target": "Impact"},
    {"source": "RiskAssessment", "relation": "HAS_EXPOSURE", "target": "Exposure"},
    {"source": "RiskAssessment", "relation": "HAS_CONFIDENCE", "target": "Confidence"}
  ]
}

⸻

Step 9: Add validation rules

{
  "validation_rules": {
    "llm_may_not_create_entity_types": true,
    "llm_may_not_create_relationship_types": true,
    "all_entities_must_use_declared_types": true,
    "all_relationships_must_match_declared_triples": true,
    "all_entities_must_have_source": true,
    "all_relationships_must_have_evidence": true,
    "all_relationships_must_have_confidence": true,
    "unknown_allowed_when_uncertain": true,
    "attack_techniques_should_use_attack_ids_when_available": true,
    "aadapt_techniques_should_use_aadapt_ids_when_available": true,
    "vulnerabilities_should_use_cve_ids_when_available": true,
    "weaknesses_should_use_cwe_ids_when_available": true,
    "risk_assessments_must_include_likelihood_impact_exposure_confidence": true,
    "risk_scores_must_include_driver_explanations": true,
    "low_confidence_facts_require_review": true
  }
}

This is the part that makes it “elite”: not the class list, but the constraints.

⸻

Step 10: Add source reliability tiers

{
  "source_reliability": {
    "tier_1": [
      "OASIS STIX",
      "MITRE ATT&CK",
      "MITRE AADAPT",
      "CISA KEV",
      "NIST NVD",
      "official project postmortem",
      "official security advisory"
    ],
    "tier_2": [
      "reputable security research",
      "blockchain analytics report",
      "auditor report",
      "incident analysis by established security firm"
    ],
    "tier_3": [
      "news article",
      "blog",
      "social media",
      "forum post"
    ]
  }
}

Rule:

Tier 3 may generate leads.
Tier 3 alone should not create high-confidence graph truth.

⸻

Step 11: Add versioning policy

{
  "versioning_policy": {
    "v1_0": "Stable reusable core",
    "minor_version": "Add non-breaking classes, relationships, aliases, mappings, or competency questions",
    "major_version": "Breaking schema changes",
    "new_class_rule": "Add a new class only if at least three distinct incident families cannot be represented without it",
    "new_relationship_rule": "Add a new relationship only if it answers a competency question and cannot be modelled with existing relationships",
    "deprecation_rule": "Do not delete immediately; mark deprecated and migrate instances"
  }
}

This prevents ontology chaos.

⸻

Step 12: Create a validator

The validator checks:

Is entity type allowed?
Is relationship type allowed?
Does source type match relationship source type?
Does target type match relationship target type?
Does relationship include evidence?
Does relationship include confidence?
Is ATT&CK ID valid if present?
Is AADAPT ID valid if present?
Is CVE/CWE valid if present?

Minimal Python logic:

def validate_relationship(rel, ontology, entity_index):
    source = entity_index[rel["source"]]
    target = entity_index[rel["target"]]
    triple = {
        "source": source["type"],
        "relation": rel["relation"],
        "target": target["type"]
    }
    if triple not in ontology["relationships"]:
        return False, f"Invalid relationship: {triple}"
    if not rel.get("evidence"):
        return False, "Missing evidence"
    if "confidence" not in rel:
        return False, "Missing confidence"
    return True, "OK"

For a serious RDF/OWL implementation, use SHACL. SHACL is designed specifically to validate RDF graphs against shapes/conditions.  

⸻

Step 13: Use the LLM only after the ontology is frozen

Your extraction prompt should say:

You are an ontology mapping engine.
Use only Digital Asset Threat Intelligence Ontology v1.0.
Do not create new entity types.
Do not create new relationship types.
Do not infer facts without evidence.
Every entity must include exact supporting text.
Every relationship must include exact supporting text.
If uncertain, use UNKNOWN or set confidence below 0.5.
Return valid JSON only.

This is correct.

Bad:

Create an ontology for this incident.

Good:

Map this incident into the existing ontology.

⸻

Step 14: Build the knowledge graph

Ontology:

DigitalAsset DEPLOYED_ON Blockchain
Incident USES AADAPTTechnique
RiskAssessment ASSESSES DigitalAsset

Knowledge graph:

JPMD DEPLOYED_ON Base
Incident_001 USES ADT3028_Siphon_Funds
RiskAssessment_001 ASSESSES JPMD

The ontology is the schema. The knowledge graph is the data.

⸻

Step 15: Use this graph build pipeline

1. Ingest source
2. Store source metadata
3. Clean and chunk text
4. Extract candidate entities with local Ollama
5. Extract candidate relationships with local Ollama
6. Validate JSON schema
7. Validate ontology classes and relationships
8. Validate ATT&CK/AADAPT/CVE/CWE mappings
9. Deduplicate entities
10. Score confidence
11. Store accepted nodes and edges
12. Store rejected candidates for review
13. Visualise graph in Cytoscape
14. Query graph with natural language
15. Compute digital asset risk assessment

The crucial point:

LLM → candidate
Validator → truth gate
Graph → accepted knowledge

⸻

Step 16: Test the ontology against incident families

Before calling it reusable, test it against:

1. Smart contract exploit
2. Bridge exploit
3. Oracle manipulation
4. Private key theft
5. Wallet compromise
6. Custody compromise
7. Exchange account takeover
8. Phishing/social engineering
9. Governance attack
10. Sequencer/L2 outage or censorship risk
11. Validator/consensus attack
12. Tokenized MMF liquidity/redemption event
13. Stablecoin depeg or reserve concern
14. Address poisoning or transaction manipulation
15. Funds laundering / siphoning path

If all can be represented without adding new ontology classes, your v1.0 is reusable.

⸻

Step 17: Acceptance criteria

Call it v1.0 only when:

It answers all competency questions.
It represents all 15 incident families.
It reuses STIX/ATT&CK/AADAPT/CVE/CWE/KEV where appropriate.
It has stable classes.
It has stable relationships.
It has validation rules.
It has source provenance.
It has confidence scoring.
It separates ontology classes from graph instances.
It prevents LLM-created classes.
It supports risk scoring without changing the ontology.

⸻

Final correct architecture

Standards
  ├── STIX 2.1 = CTI object model and exchange
  ├── ATT&CK = general adversary behaviour
  ├── AADAPT = digital asset adversary behaviour
  ├── CVE/CWE/KEV = vulnerability grounding
  ↓
Reusable Ontology v1.0
  ├── CTI core
  ├── Behaviour layer
  ├── Digital asset infrastructure layer
  └── Asset/risk layer
  ↓
Validation Layer
  ├── JSON schema / SHACL
  ├── controlled entity types
  ├── controlled relationships
  ├── evidence required
  └── confidence required
  ↓
Knowledge Graph
  ├── incidents
  ├── assets
  ├── actors
  ├── techniques
  ├── infrastructure
  ├── evidence
  └── risk assessments

The most important sentence:

Elite ontology engineering does not ask the LLM to invent the ontology per incident. It creates a stable, versioned, standards-aligned ontology first, then uses the LLM only to map new evidence into that ontology under strict validation rules.