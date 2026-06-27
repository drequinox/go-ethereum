# Knowledge Graphs from Multiple Data Sources — a runnable end-to-end tutorial

A four-step pipeline that ingests heterogeneous data, builds an ontology and
knowledge graph (first by hand, then with an LLM), shows why a graph beats an
RDBMS for relationship analysis, and renders an interactive explorer.

The worked example is a small blockchain ecosystem (a DAO, a DEX, an NFT
marketplace, two exchanges, and five people), and the motivating question is:

> **"Given a blockchain address, how does it relate to other entities on the
> network?"**

## Run order

```bash
pip install networkx

python 01_manual_kg.py      # hand-built ontology + multi-source ingest + traversals
python 02_kg_vs_rdbms.py    # same questions in SQLite vs graph; honest benchmark
python 03_llm_extraction.py # LLM proposes ontology + extracts from prose; validated & merged
python 04_visualize.py      # emits output/kg_explorer.html — open in any browser
```

Step 3 runs offline using a cached LLM response (so the demo never depends on
a network call). To run it live: `ANTHROPIC_API_KEY=sk-... python 03_llm_extraction.py`

## The three data sources (deliberately different shapes)

| File | Shape | What it knows |
|------|-------|---------------|
| `data/transactions.csv` | structured table | WHO sent WHAT to WHOM (the money trail) |
| `data/entity_labels.json` | semi-structured JSON | WHO OPERATES each address (Coinbase, AquaSwap, the DAO...) |
| `data/ecosystem_notes.txt` | unstructured prose | WHY: grants, memberships, the people behind the wallets |

Each fact lives in exactly one source. The unified graph answers questions
that span all three — e.g. *"explain the 25,000 USDC transfer to 0xALICE"*:
the CSV has the transfer, the JSON identifies the treasury as Lighthouse DAO,
and only the prose knows Alice owns that wallet and received a grant.

## The conceptual through-line

1. **A knowledge graph has three layers.** The **ontology** is the schema of
   *meaning*: node types (Wallet, SmartContract, Token, Entity, Person) and
   the typed, directional relationships permitted between them. **Entities**
   are typed nodes; **relationships** are typed, directed, attribute-carrying
   edges. An RDBMS schema only crudely approximates the ontology layer.
2. **Why a graph and not an RDBMS:** "what does this address relate to?" is
   *variable-depth traversal over heterogeneous relationship types*. That is
   the graph's native operation and the RDBMS's recursive-CTE worst case —
   script 02 shows the identical question both ways and benchmarks it.
3. **The LLM's role (script 03):** the LLM *proposes* the ontology from raw
   text, then *extracts* instances that must conform to it. Plain code — not
   the model — validates every triple against the ontology and demands a
   verbatim evidence span. **The LLM proposes; the validator disposes.** The
   cached response deliberately contains one invalid triple so you can watch
   the gate reject it during the demo.
4. **Entity resolution** is where multi-source integration happens: same
   address or same canonical name ⇒ same node. Wallets mentioned in prose
   merge onto wallets from the CSV; organisations in prose merge onto the
   JSON directory entries.

## Suggested 10-minute team demo script

1. Open the three data files side by side — point out the three shapes.
2. Run `01` — show the ontology dict, then Q1: "0xALICE's direct
   relationships, with the operator behind each counterparty."
3. Run `02` — show the recursive CTE next to `nx.descendants(...)`; let the
   benchmark print. Mention the verdict: graph for analysis, RDBMS for
   aggregation; production runs both.
4. Run `03` — show the LLM-proposed ontology, the REJECTED line (the
   validation gate working), and the cross-source "explain the 25,000 USDC
   transfer" answer.
5. Open `output/kg_explorer.html` — type `0xALICE`, hops = 2, click **Show
   neighbourhood**. Then click the `Alice` person node and show the verbatim
   evidence span from the prose. Toggle type filters to show heterogeneity.

## Going to production

- Swap `networkx` for **Neo4j** or **Memgraph** (persistence, Cypher,
  index-free adjacency at scale); keep the same four-phase LLM architecture.
- Express the ontology in **OWL/RDFS**, or validate instances with **SHACL**,
  if you need formal reasoning.
- Harden entity resolution: alias tables, fuzzy matching, embedding
  similarity — exact-match resolution (used here for clarity) is the naive
  baseline.
- For real chains, feed the CSV stage from a node RPC, Etherscan-style APIs,
  or a Dune/BigQuery export; the rest of the pipeline is unchanged.
