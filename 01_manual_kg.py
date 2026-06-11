"""
01_manual_kg.py — Build a knowledge graph BY HAND from multiple data sources.

A knowledge graph has three layers, and it pays to keep them distinct:

  1. ONTOLOGY  (the schema of meaning): what TYPES of things exist
     (Wallet, SmartContract, Token, Entity, Person...) and what TYPES of
     relationships are allowed between them (TRANSFERRED, CONTROLS,
     DEPLOYED...). An RDBMS schema only crudely approximates this.

  2. ENTITIES  (the nodes): concrete instances — 0xALICE, AquaSwap, ART token.

  3. RELATIONSHIPS (the edges): typed, directed, attribute-carrying facts —
     (0xALICE) -[TRANSFERRED {usd: 5000, asset: USDC}]-> (0xDEX_POOL).

We ingest TWO differently-shaped sources into ONE graph, then ask the
question that motivates everything: "given an address, what does it relate
to on the network?"

Run:  python 01_manual_kg.py
"""

import csv
import json
import networkx as nx

# ---------------------------------------------------------------------------
# 1. THE ONTOLOGY — written by hand. In production this would live in
#    OWL/RDFS or a property-graph schema; a dict is enough to see the idea.
# ---------------------------------------------------------------------------
ONTOLOGY = {
    "node_types": {
        "Wallet":        {"props": ["address", "chain"]},
        "SmartContract": {"props": ["address", "purpose"]},
        "Token":         {"props": ["symbol", "standard"]},
        "Entity":        {"props": ["name", "category"]},   # exchange, DAO, marketplace
        "Person":        {"props": ["name", "role"]},
    },
    "edge_types": {
        # (source type, relationship, target type)
        ("Wallet",        "TRANSFERRED", "Wallet"),
        ("Wallet",        "TRANSFERRED", "SmartContract"),
        ("SmartContract", "TRANSFERRED", "Wallet"),
        ("Entity",        "CONTROLS",    "Wallet"),
        ("Entity",        "CONTROLS",    "SmartContract"),
        ("Wallet",        "DEPLOYED",    "Token"),
        ("Person",        "OWNS",        "Wallet"),
    },
}


def assert_edge_allowed(g, u, rel, v):
    """Toy ontology validator: refuse edges the ontology doesn't license."""
    key = (g.nodes[u]["type"], rel, g.nodes[v]["type"])
    if key not in ONTOLOGY["edge_types"]:
        raise ValueError(f"Ontology violation: {key} not a permitted relationship")


# ---------------------------------------------------------------------------
# 2. INGESTION — two sources, two shapes, ONE graph.
#    Entities merge on their natural identity (the address) — no JOINs.
# ---------------------------------------------------------------------------
g = nx.MultiDiGraph()   # multi: many transfers can link the same pair

# We read the label feed FIRST so we know which addresses are contracts.
feed = json.load(open("data/entity_labels.json"))
contract_addrs = {l["address"] for l in feed["labels"] if l.get("contract")}


def ensure_address(addr, chain=None):
    if addr not in g:
        ntype = "SmartContract" if addr in contract_addrs else "Wallet"
        g.add_node(addr, type=ntype, label=addr, chain=chain)


# --- Source A: the transfer ledger (CSV) -----------------------------------
with open("data/transactions.csv") as f:
    for row in csv.DictReader(f):
        ensure_address(row["from_address"], row["chain"])
        ensure_address(row["to_address"], row["chain"])
        g.add_edge(row["from_address"], row["to_address"], rel="TRANSFERRED",
                   asset=row["asset"], amount=float(row["amount"]),
                   usd=float(row["amount_usd"]), tx=row["tx_hash"],
                   ts=row["timestamp"])

# --- Source B: the entity directory (JSON) ---------------------------------
for lab in feed["labels"]:
    ensure_address(lab["address"])
    ent = lab["entity"]
    if ent not in g:
        g.add_node(ent, type="Entity", label=ent, category=lab["category"])
    g.add_edge(ent, lab["address"], rel="CONTROLS")
    assert_edge_allowed(g, ent, "CONTROLS", lab["address"])

for tok in feed["tokens"]:
    if tok["symbol"] not in g:
        g.add_node(tok["symbol"], type="Token", label=tok["name"],
                   standard=tok["standard"], contract=tok["contract"])
    if tok.get("deployer"):
        ensure_address(tok["deployer"])
        g.add_edge(tok["deployer"], tok["symbol"], rel="DEPLOYED")
        assert_edge_allowed(g, tok["deployer"], "DEPLOYED", tok["symbol"])

print(f"Graph built: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges\n")

# ---------------------------------------------------------------------------
# 3. THE MOTIVATING QUERY: "given an address, what does it relate to?"
# ---------------------------------------------------------------------------
ADDR = "0xALICE"

# Q1: One-hop view — direct counterparties, with the entity BEHIND each one.
print(f"Q1  Direct relationships of {ADDR}:")
seen = set()
for u, v, d in list(g.out_edges(ADDR, data=True)) + list(g.in_edges(ADDR, data=True)):
    other = v if u == ADDR else u
    arrow = "->" if u == ADDR else "<-"
    key = (other, arrow, d["rel"])
    if key in seen:
        continue
    seen.add(key)
    behind = [e for e, w, dd in g.in_edges(other, data=True) if dd["rel"] == "CONTROLS"]
    tag = f"  (operated by {behind[0]})" if behind else ""
    print(f"    {ADDR} {arrow} [{d['rel']}] {arrow} {other}{tag}")

# Q2: Two-hop neighbourhood — the "everything it touches, and what touches
#     those" view. ego_graph IS this question, in one call.
ego = nx.ego_graph(g.to_undirected(as_view=False), ADDR, radius=2)
print(f"\nQ2  Everything within 2 hops of {ADDR} "
      f"({ego.number_of_nodes()} nodes):")
print("   ", sorted(ego.nodes()))

# Q3: How are two addresses related, if at all? Path finding across
#     HETEROGENEOUS relationship types — transfers AND control AND deployment.
print(f"\nQ3  How is {ADDR} related to 0xCAROL?")
und = g.to_undirected(as_view=False)
path = nx.shortest_path(und, ADDR, "0xCAROL")
parts = []
for a, b in zip(path, path[1:]):
    rel = list(und.get_edge_data(a, b).values())[0]["rel"]
    parts.append(f"{a} ~[{rel}]~ ")
print("    " + "".join(parts) + path[-1])

# Q4: Aggregate + structure together: which entities ultimately received
#     funds that originated from the DAO treasury? (variable-depth taint)
flow = nx.subgraph_view(g, filter_edge=lambda u, v, k: g[u][v][k]["rel"] == "TRANSFERRED")
downstream = nx.descendants(flow, "0xDAO_TREASURY")
print(f"\nQ4  Addresses downstream of the DAO treasury (any depth): "
      f"{sorted(downstream)}")
operators = sorted({e for addr in downstream
                    for e, w, dd in g.in_edges(addr, data=True)
                    if dd["rel"] == "CONTROLS"})
print(f"    Entities operating those addresses: {operators}")

# Persist for later steps
with open("output/manual_kg.json", "w") as f:
    json.dump(nx.node_link_data(g, edges="links"), f, indent=2, default=str)
print("\nSaved -> output/manual_kg.json")
