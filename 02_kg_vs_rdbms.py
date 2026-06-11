"""
02_kg_vs_rdbms.py — The same questions asked of an RDBMS and of a graph.

The question driving everything: "given address X, what is it connected to,
directly and indirectly?" That is a VARIABLE-DEPTH TRAVERSAL question, and
it exposes the structural difference between the two models:

  1. EXPRESSIVENESS  — in SQL, multi-hop reachability is a recursive CTE you
     hand-write per question, with a depth bound you must guess. In a graph,
     traversal is the primitive operation (one function call).
  2. SCHEMA RIGIDITY — adding a new relationship type (CONTROLS, DEPLOYED,
     STAKED_WITH...) means a new table and new joins in every query that
     should see it. In a graph it's just a new edge type, and existing
     traversals pick it up automatically.
  3. PERFORMANCE SHAPE — a join scans index structures over the WHOLE table
     per hop; graph traversal touches only the neighbourhood it explores.
  4. HETEROGENEITY — wallets, contracts, tokens, entities, people in an
     RDBMS = five tables and a different join path for every question.
     In a graph they coexist in one structure.

Run:  python 02_kg_vs_rdbms.py
"""

import csv
import random
import sqlite3
import time

import networkx as nx

# ---------------------------------------------------------------------------
# Load the same small ledger into BOTH representations
# ---------------------------------------------------------------------------
rows = list(csv.DictReader(open("data/transactions.csv")))

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE transfers (tx_hash TEXT, ts TEXT, from_addr TEXT, to_addr TEXT,
                        asset TEXT, amount_usd REAL);
CREATE TABLE labels (address TEXT PRIMARY KEY, entity TEXT, category TEXT);
CREATE INDEX idx_from ON transfers(from_addr);
""")
db.executemany("INSERT INTO transfers VALUES (?,?,?,?,?,?)",
               [(r["tx_hash"], r["timestamp"], r["from_address"],
                 r["to_address"], r["asset"], float(r["amount_usd"]))
                for r in rows])
db.executemany("INSERT INTO labels VALUES (?,?,?)", [
    ("0xDEX_POOL", "AquaSwap", "dex_pool"),
    ("0xCEX_DEP1", "Coinbase", "exchange_deposit"),
    ("0xCEX_DEP2", "Kraken", "exchange_deposit"),
    ("0xDAO_TREASURY", "Lighthouse DAO", "dao_treasury"),
])

g = nx.DiGraph()
for r in rows:
    g.add_edge(r["from_address"], r["to_address"], usd=float(r["amount_usd"]))

# ---------------------------------------------------------------------------
# QUESTION: "Every address reachable from 0xDAO_TREASURY, at ANY depth,
#            with the entity (if known) behind each one."
# ---------------------------------------------------------------------------
print("=" * 74)
print("SQL version — a recursive CTE you must hand-write (per question!):")
print("=" * 74)
SQL = """
WITH RECURSIVE reach(addr, depth, path) AS (
    SELECT '0xDAO_TREASURY', 0, '0xDAO_TREASURY'
  UNION
    SELECT t.to_addr, reach.depth + 1, reach.path || ' -> ' || t.to_addr
    FROM transfers t JOIN reach ON t.from_addr = reach.addr
    WHERE reach.depth < 10            -- you must guess a depth bound!
)
SELECT DISTINCT reach.addr, reach.depth, l.entity, reach.path
FROM reach LEFT JOIN labels l ON l.address = reach.addr
WHERE reach.depth > 0 ORDER BY reach.depth;
"""
print(SQL)
for addr, depth, entity, path in db.execute(SQL):
    print(f"  d={depth}  {addr:<16} {entity or ''}")

print()
print("=" * 74)
print("Graph version — reachability IS the primitive:")
print("=" * 74)
print(">>> nx.descendants(g, '0xDAO_TREASURY')\n")
print(f"  {sorted(nx.descendants(g, '0xDAO_TREASURY'))}")
print("\n  ...and the connecting path between any two addresses:")
print(">>> nx.shortest_path(g, '0xDAO_TREASURY', '0xCEX_DEP1')")
print(f"  {nx.shortest_path(g, '0xDAO_TREASURY', '0xCEX_DEP1')}")

# ---------------------------------------------------------------------------
# THE PERFORMANCE SHAPE, at a scale where it matters:
# 500,000 transfers across 50,000 addresses; trace one address's reach.
# ---------------------------------------------------------------------------
print()
print("=" * 74)
print("Scale test: 500,000 synthetic transfers, 50,000 addresses, depth 6")
print("=" * 74)
random.seed(42)
N_W, N_T = 50_000, 500_000
synth = [(f"w{random.randrange(N_W)}", f"w{random.randrange(N_W)}")
         for _ in range(N_T)]

db.execute("CREATE TABLE big (from_addr TEXT, to_addr TEXT)")
db.executemany("INSERT INTO big VALUES (?,?)", synth)
db.execute("CREATE INDEX idx_big_from ON big(from_addr)")

G = nx.DiGraph()
G.add_edges_from(synth)

src, DEPTH = "w0", 6

t0 = time.perf_counter()
sql_n = db.execute(f"""
WITH RECURSIVE reach(addr, depth) AS (
    SELECT ?, 0
  UNION
    SELECT b.to_addr, reach.depth+1
    FROM big b JOIN reach ON b.from_addr = reach.addr
    WHERE reach.depth < {DEPTH})
SELECT COUNT(DISTINCT addr) FROM reach""", (src,)).fetchone()[0]
t_sql = time.perf_counter() - t0

t0 = time.perf_counter()
bfs = nx.single_source_shortest_path_length(G, src, cutoff=DEPTH)
t_graph = time.perf_counter() - t0

print(f"  SQL recursive CTE, depth {DEPTH}:  {sql_n:>6} addresses  "
      f"in {t_sql*1000:8.1f} ms")
print(f"  Graph BFS,        depth {DEPTH}:  {len(bfs):>6} addresses  "
      f"in {t_graph*1000:8.1f} ms")
print(f"  Speedup: {t_sql/t_graph:,.1f}x in-memory — and note this FLATTERS SQL:")
print("  one relationship type, one table, an ideal index. Add CONTROLS,")
print("  DEPLOYED and OWNS tables and every hop becomes a multi-table join;")
print("  the gap compounds per relationship type. A disk-backed RDBMS also")
print("  pays I/O per join that a native graph store (index-free adjacency)")
print("  does not.")

print("""
Verdict for address/relationship analysis:
  - "Given an address, show its counterparties, the entities behind them,
     and everything reachable from it" is a TRAVERSAL question.
  - RDBMS: per-question recursive CTEs, guessed depth bounds, join cost
    over global tables, a schema migration for every new relationship type.
  - Knowledge graph: traversal is native, depth is unbounded, new edge
    types compose with existing queries, heterogeneous node types
    (Wallet / Contract / Token / Entity / Person) live in one structure.
  - Keep the RDBMS for what it is genuinely good at: bulk storage,
    aggregation, reporting ("total USD volume per day"). Production
    systems run BOTH: the ledger in SQL/columnar, the analytics in the
    graph, with a sync pipeline between them.
""")
