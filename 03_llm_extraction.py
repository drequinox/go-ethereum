"""
03_llm_extraction.py — Let an LLM discover the ontology and populate the graph
from UNSTRUCTURED text, then merge with the structured-source graph of step 1.

The architecture matters more than any single prompt:

  PHASE 1  ONTOLOGY PROPOSAL   The LLM reads the corpus and proposes node
                               types, edge types and their domain/range
                               constraints. A human reviews it ONCE; it then
                               becomes the contract for everything after.

  PHASE 2  TYPED EXTRACTION    The LLM extracts entity and relationship
                               INSTANCES that must conform to the phase-1
                               ontology. Extracting against a fixed schema
                               dramatically reduces hallucinated structure.

  PHASE 3  VALIDATION GATE     Plain code rejects any triple whose types the
                               ontology doesn't license, and anything without
                               a verbatim evidence span from the source text.
                               The LLM proposes; the validator disposes.

  PHASE 4  ENTITY RESOLUTION   Merge into the existing graph: same address or
  + MERGE                      same canonical name => same node. This is where
                               "multiple sources, one graph" pays off.

Run:  ANTHROPIC_API_KEY=sk-... python 03_llm_extraction.py
      (without a key it uses data/llm_cached_response.json so the demo
       runs end to end offline)
"""

import json
import os
import urllib.request

import networkx as nx

NOTES = open("data/ecosystem_notes.txt").read()
API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def claude(prompt, system=""):
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        method="POST",
        headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        data=json.dumps({
            "model": "claude-sonnet-4-5", "max_tokens": 4000,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }).encode())
    with urllib.request.urlopen(req) as r:
        out = json.loads(r.read())
    text = "".join(b["text"] for b in out["content"] if b["type"] == "text")
    return json.loads(text.replace("```json", "").replace("```", "").strip())


# ---------------------------------------------------------------------------
# PHASE 1 — ontology proposal
# ---------------------------------------------------------------------------
ONTOLOGY_PROMPT = f"""Read the following text corpus. Propose a property-graph
ontology for it: the minimal set of node types and edge types needed to
represent every fact in the text.

Respond with ONLY a JSON object, no prose, no markdown fences:
{{
  "node_types": {{"TypeName": {{"description": "...", "props": ["..."]}}}},
  "edge_types": [
    {{"rel": "REL_NAME", "domain": "SourceType", "range": "TargetType",
      "description": "..."}}
  ]
}}
Rules: edge names UPPER_SNAKE_CASE; node types PascalCase; prefer reusing a
general type over inventing near-duplicates; every type must be justified by
the text.

CORPUS:
{NOTES}"""


# ---------------------------------------------------------------------------
# PHASE 2 — typed extraction against the agreed ontology
# ---------------------------------------------------------------------------
def extraction_prompt(ontology):
    return f"""Extract the knowledge graph from the text below, conforming
EXACTLY to this ontology:

{json.dumps(ontology, indent=2)}

Respond with ONLY a JSON object, no prose, no markdown fences:
{{
  "entities": [
    {{"id": "stable_snake_case_id", "type": "<node type from ontology>",
      "label": "human-readable name", "props": {{...}},
      "evidence": "<short verbatim span from the text that grounds this>"}}
  ],
  "relationships": [
    {{"source": "<entity id>", "rel": "<edge type from ontology>",
      "target": "<entity id>",
      "evidence": "<short verbatim grounding span>"}}
  ]
}}
Rules: every entity and relationship MUST carry an evidence span actually
present in the text. Do not invent facts not stated in the text. Use wallet
addresses verbatim as labels where they appear.

TEXT:
{NOTES}"""


if API_KEY:
    print("Phase 1: asking the LLM to propose an ontology...")
    ontology = claude(ONTOLOGY_PROMPT,
                      system="You are an information-extraction system. "
                             "Output strictly valid JSON.")
    print("Phase 2: typed extraction against the proposed ontology...")
    extraction = claude(extraction_prompt(ontology),
                        system="You are an information-extraction system. "
                               "Output strictly valid JSON.")
    json.dump({"ontology": ontology, "extraction": extraction},
              open("output/llm_response.json", "w"), indent=2)
else:
    print("No ANTHROPIC_API_KEY set — using cached LLM response "
          "(data/llm_cached_response.json)\n")
    cached = json.load(open("data/llm_cached_response.json"))
    ontology, extraction = cached["ontology"], cached["extraction"]

print(f"Ontology proposed by the LLM: {len(ontology['node_types'])} node "
      f"types, {len(ontology['edge_types'])} edge types")
for e in ontology["edge_types"]:
    print(f"    ({e['domain']}) -[{e['rel']}]-> ({e['range']})")

# ---------------------------------------------------------------------------
# PHASE 3 — validation gate (code, not vibes)
# ---------------------------------------------------------------------------
allowed = {(e["domain"], e["rel"], e["range"]) for e in ontology["edge_types"]}
node_types = set(ontology["node_types"])
by_id = {e["id"]: e for e in extraction["entities"]}

valid_entities, valid_rels, rejected = [], [], []
for ent in extraction["entities"]:
    if ent["type"] in node_types and ent.get("evidence"):
        valid_entities.append(ent)
    else:
        rejected.append(("entity", ent["id"], "unknown type or no evidence"))

ok_ids = {e["id"] for e in valid_entities}
for r in extraction["relationships"]:
    s, t = by_id.get(r["source"]), by_id.get(r["target"])
    if not (r["source"] in ok_ids and r["target"] in ok_ids):
        rejected.append(("rel", f"{r['source']}-{r['rel']}->{r['target']}",
                         "dangling endpoint"))
    elif (s["type"], r["rel"], t["type"]) not in allowed:
        rejected.append(("rel", f"{s['type']}-{r['rel']}->{t['type']}",
                         "not licensed by ontology"))
    elif not r.get("evidence"):
        rejected.append(("rel", r["rel"], "no evidence span"))
    else:
        valid_rels.append(r)

print(f"\nValidation: {len(valid_entities)} entities and {len(valid_rels)} "
      f"relationships admitted; {len(rejected)} rejected")
for kind, what, why in rejected:
    print(f"    REJECTED {kind}: {what}  ({why})")

# ---------------------------------------------------------------------------
# PHASE 4 — entity resolution + merge with the structured-source KG
# ---------------------------------------------------------------------------
g = nx.MultiDiGraph()
data = json.load(open("output/manual_kg.json"))
for n in data["nodes"]:
    g.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
for l in data["links"]:
    g.add_edge(l["source"], l["target"],
               **{k: v for k, v in l.items()
                  if k not in ("source", "target", "key")})


def resolve(ent):
    """Same wallet address, or same canonical label => same node.
    (Production: fuzzy matching, alias tables, embedding similarity.)"""
    for node, d in g.nodes(data=True):
        if ent["label"] == node or ent["label"] == d.get("label"):
            return node
        if ent["props"].get("address") and ent["props"]["address"] == node:
            return node
    return None


id_to_node, new_nodes = {}, 0
for ent in valid_entities:
    node = resolve(ent)
    if node is None:
        node = ent["label"]
        g.add_node(node, type=ent["type"], label=ent["label"],
                   source="llm", evidence=ent["evidence"], **ent["props"])
        new_nodes += 1
    else:
        g.nodes[node].setdefault("evidence", ent["evidence"])
        g.nodes[node]["enriched_by_llm"] = True
    id_to_node[ent["id"]] = node

new_edges = 0
for r in valid_rels:
    u, v = id_to_node[r["source"]], id_to_node[r["target"]]
    if not any(d.get("rel") == r["rel"]
               for d in (g.get_edge_data(u, v) or {}).values()):
        g.add_edge(u, v, rel=r["rel"], source="llm", evidence=r["evidence"])
        new_edges += 1

print(f"\nMerge: +{new_nodes} new nodes, +{new_edges} new edges from "
      f"unstructured text; existing nodes enriched in place.")
print(f"Unified graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")

# ---------------------------------------------------------------------------
# THE PAYOFF — a question no single source can answer:
# "WHY did the treasury send 25,000 USDC to 0xALICE, and WHO is behind it?"
#   - the transfer amount lives only in the CSV
#   - the treasury<->Lighthouse DAO link lives only in the JSON directory
#   - the grant, and the person behind the wallet, live only in the prose
# ---------------------------------------------------------------------------
print("\nCross-source answer — 'explain the 25,000 USDC transfer':")
for u, v, d in g.edges(data=True):
    if d.get("rel") == "TRANSFERRED" and d.get("usd") == 25000:
        print(f"    {u} -[TRANSFERRED ${d['usd']:,.0f} {d['asset']}]-> {v}   [CSV]")
for u, v, d in g.edges(data=True):
    if d.get("rel") in ("OWNS_WALLET", "OWNS"):
        print(f"    {u} -[{d['rel']}]-> {v}   [LLM, prose]")
        break
for u, v, d in g.edges(data=True):
    if d.get("rel") == "RECEIVED_GRANT_FROM":
        print(f"    {u} -[RECEIVED_GRANT_FROM]-> {v}   [LLM, prose]")
        print(f"        evidence: \"{d['evidence']}\"")

with open("output/unified_kg.json", "w") as f:
    json.dump(nx.node_link_data(g, edges="links"), f, indent=2, default=str)
print("\nSaved -> output/unified_kg.json")
