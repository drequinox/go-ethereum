# Mastering Knowledge Graphs

### From raw data to LLM-built ontologies — a hands-on tutorial

This tutorial teaches you to ingest heterogeneous data, design an ontology, build a knowledge graph, use a large language model to construct one automatically, reason about why a graph beats a relational database for relationship analysis, and visualise the result interactively. It is paired with four runnable Python scripts (`01`–`04`) and a small blockchain ecosystem dataset; read the prose here, run the scripts as you go, and do the exercises. By the end you will be able to design and defend a knowledge-graph solution from first principles rather than by imitation.

The running example is a small on-chain world — a DAO treasury, a decentralised exchange, an NFT marketplace, two centralised exchanges, and four people — and the question that drives everything is deliberately concrete: **given a blockchain address, how is it related to everything else on the network?** We keep that question in view at every step, because the entire argument for knowledge graphs rests on it.

---

## How to use this tutorial

Work through it in order. Each part builds a layer of understanding that the next part depends on, and the four scripts map onto the four parts that do the building:

| Part | Theme | Script |
|------|-------|--------|
| I | Foundations and mental models | — |
| II | Building a graph by hand | `01_manual_kg.py` |
| III | Why a graph and not an RDBMS | `02_kg_vs_rdbms.py` |
| IV | Letting an LLM build the graph | `03_llm_extraction.py` |
| V | Visualisation and querying | `04_visualize.py` |
| VI | Production and the road to mastery | — |

Run the first script now, before reading further, so the rest of the tutorial describes something you have already seen move:

```bash
pip install networkx
python 01_manual_kg.py
```

---

# Part I — Foundations

## 1. The shape of the problem

Most data we collect is *relational* in the plain-English sense: it is about how things connect. A wallet sends funds to another wallet. A person owns a wallet. A marketplace routes a fee to a treasury. An artist deploys a token. When we ask useful questions of this data, we are almost never asking about a single row in isolation. We are asking about **paths**: who is this address connected to, how does money reach an exchange, what links these two accounts, who ultimately benefits from this flow.

The defining feature of these questions is that the answer has **unknown depth and unknown type**. "Show me everything connected to address X" does not specify how many hops away the connections lie, nor which kinds of relationship to follow. You might follow a transfer, then an ownership link, then a fee agreement, then a grant — four different relationship types in a single chain of reasoning. A data model that forces you to know the depth and the relationship types in advance fights you on every such question. A data model where traversal of arbitrary depth across heterogeneous relationships is the *native* operation answers them effortlessly. That difference is the whole tutorial in one sentence, and everything below is an unpacking of it.

## 2. What a knowledge graph actually is

A knowledge graph is not merely "data drawn as dots and lines." It is a structure with three distinct layers, and confusing them is the most common reason people build bad graphs. Hold the three apart in your mind.

The **ontology** is the schema of *meaning*. It declares what *types* of things may exist in your world — in our case Wallet, SmartContract, Token, Entity, Person — and, crucially, which *types* of relationship are permitted to hold between which types of thing. A wallet may TRANSFER to another wallet; a person may OWN a wallet; an entity may CONTROL a contract. The ontology is a contract about what is *sayable*. It is the layer that distinguishes a knowledge graph from a mere network diagram, because it carries semantics: a relationship is not just an edge, it is an edge of a named kind with a defined domain (the type it starts from) and range (the type it points to).

The **entities** are the concrete instances — the nodes. `0xALICE` is an instance of Wallet; `AquaSwap` is an instance of Entity; the `ART` token is an instance of Token. Entities are the *nouns* of your graph, and each one carries properties: an address, a chain, a category, a human-readable label.

The **relationships** are the typed, directed, attribute-carrying facts — the edges. The edge from `0xALICE` to `0xDEX_POOL` is not bare; it is a TRANSFERRED edge carrying `{asset: USDC, usd: 5000, tx: 0x0002}`. Relationships are the *verbs*, and because they are first-class objects that hold their own attributes, the graph can record not merely *that* two things are connected but *how*, *when*, and *how much*.

Read those three paragraphs again with the example in front of you, because the rest of your mastery is built on keeping ontology, entities, and relationships separate. When we let an LLM build a graph later, the single most important design decision is forcing it to settle the *ontology* first and only then extract *entities* and *relationships* that conform to it. Skip that discipline and you get a tangle of dots and lines with no semantics, which is exactly the "knowledge graph" that disappoints people and gets abandoned.

A note on vocabulary, so the literature does not confuse you. The academic and Semantic-Web tradition expresses graphs as **RDF triples** — subject, predicate, object — with ontologies written in **RDFS** or **OWL**, queried with **SPARQL**, and stored in **triple stores**. The industry tradition uses **labelled property graphs**, where nodes and edges both carry key-value properties, queried with **Cypher** or **Gremlin**, and stored in engines like **Neo4j** or **Memgraph**. They are two dialects of the same idea. This tutorial uses the property-graph model because it is the more intuitive entry point and maps directly onto Python dictionaries, but everything you learn transfers; Part VI shows the production shape of both.

## 3. Graphs versus relational databases — the real distinction

You almost certainly know relational databases, so the fastest way to understand graphs is by contrast, and we must do this carefully because the naive contrast is wrong. The wrong version says "relational databases can't do graphs." They can. SQL with recursive common table expressions is Turing-complete over your data; there is no relationship query a graph can answer that you cannot, with enough effort, coax out of an RDBMS. The real distinction is not *capability* but *fit*, and fit has four dimensions worth naming precisely.

The first is **expressiveness**. In a relational model, a multi-hop traversal is a recursive CTE that you hand-write for each question, complete with a depth bound you must guess in advance. In a graph, traversal is the primitive operation — a single function call that expresses "everything reachable from here" without you specifying depth at all. The question "what is this address connected to?" is one line in a graph and a bespoke recursive query in SQL, and you will write a *different* bespoke query for every variation of the question.

The second is **schema rigidity**. Adding a new kind of relationship to a relational model means a new table and new joins in every query that ought to see it. If today your graph knows about transfers and tomorrow you want to add "provides liquidity to" and "received a grant from," in a graph you simply start adding edges of the new types and your existing traversals pick them up automatically, because a traversal follows edges regardless of their label. In an RDBMS, every new relationship type is a schema migration and a rewrite of the queries that should now span it. Graphs are *schema-flexible* in a way that matters enormously when your understanding of the domain is still evolving — which, when you are integrating new data sources, it always is.

The third is **performance shape**. A relational join, even a well-indexed one, reasons over the structure of an entire table per hop. A graph traversal touches only the neighbourhood it actually explores. On a small dataset the difference is invisible; the database's indexes hide it. But the cost curves diverge as depth and density grow, and they diverge faster as you add relationship types, because in the relational world each additional type is another table to join at each hop. Native graph stores exploit *index-free adjacency*: each node holds direct pointers to its neighbours, so following an edge is a pointer dereference rather than an index lookup, and traversal cost depends on the size of the answer rather than the size of the database. Script `02` demonstrates this empirically — on half a million synthetic transfers, a six-hop reachability query runs several times faster as a graph traversal than as a recursive CTE, and the script is honest that even this *flatters* the relational side, because the benchmark uses a single relationship type with an ideal index.

The fourth is **heterogeneity**. Our world has wallets, contracts, tokens, organisations, and people all at once, and the interesting questions cross between them — "which entity operates the address this person sent funds to?" In a relational model these are five tables and a different join path for every such question. In a graph they are five node types in one structure, and a single traversal walks across all of them without caring which type it is currently standing on.

Hold all four in mind and the verdict writes itself, and it is not "graphs win." It is **fit**. Use a relational or columnar store for what it is genuinely best at: bulk storage, transactional integrity, and aggregation — "total USD volume per day," "count of transactions per address." Use a knowledge graph for relationship analysis — reachability, path-finding, neighbourhood exploration, pattern detection across heterogeneous links. Mature systems run both, with the ledger in SQL and the analytics in the graph, synchronised by a pipeline between them. A master does not evangelise graphs; a master knows which question each model is built to answer and reaches for the right one.

With the conceptual foundation in place, we build.

---

# Part II — Building a graph by hand

You learn an abstraction by building it without help once, so that when a tool builds it for you, you know what the tool is doing and where it can go wrong. This part walks through `01_manual_kg.py` not line by line — you have the file — but at the level of the decisions it embodies.

## 4. Ontology engineering

Everything begins with the ontology, and good ontology design is a craft worth taking seriously, because the ontology determines what questions your graph can answer and how cleanly it integrates new data.

In the script the ontology is a plain Python dictionary, and that plainness is deliberate: it strips the idea down to its essence so you see what an ontology *is* before you meet the heavyweight formalisms. It declares node types with their allowed properties, and it declares edge types as triples of `(source type, relationship, target type)`:

```python
ONTOLOGY = {
    "node_types": {
        "Wallet":        {"props": ["address", "chain"]},
        "SmartContract": {"props": ["address", "purpose"]},
        "Token":         {"props": ["symbol", "standard"]},
        "Entity":        {"props": ["name", "category"]},
        "Person":        {"props": ["name", "role"]},
    },
    "edge_types": {
        ("Wallet",        "TRANSFERRED", "Wallet"),
        ("Wallet",        "TRANSFERRED", "SmartContract"),
        ("Entity",        "CONTROLS",    "Wallet"),
        ("Wallet",        "DEPLOYED",    "Token"),
        ("Person",        "OWNS",        "Wallet"),
        # ...
    },
}
```

The edge-type declaration is the part that carries the semantics, and it deserves a name: **domain and range constraints**. The domain of CONTROLS is Entity; its range is Wallet or SmartContract. This is not decoration. It is the rule that lets a validator reject a nonsensical fact like "a Token CONTROLS a Person" before it pollutes the graph. When we hand graph construction to an LLM in Part IV, this exact mechanism — checking each proposed edge against the licensed `(source type, relationship, target type)` triples — is what keeps the model honest. The validator in the script is four lines:

```python
def assert_edge_allowed(g, u, rel, v):
    key = (g.nodes[u]["type"], rel, g.nodes[v]["type"])
    if key not in ONTOLOGY["edge_types"]:
        raise ValueError(f"Ontology violation: {key} not permitted")
```

Three principles guide good ontology design, and you should internalise them because they are where beginners go wrong.

**Prefer general types over near-duplicates.** It is tempting to mint `ExchangeWallet`, `DAOWallet`, and `UserWallet` as separate node types. Resist. They are all Wallets; what differs is a *property* (`category`) or the *entity that controls them*, not their fundamental type. A proliferation of near-identical types makes every query branch on type and defeats the heterogeneity advantage that justified the graph in the first place. Model the difference as an attribute or a relationship, not a type.

**Make relationships verbs, and direction meaningful.** CONTROLS, OWNS, DEPLOYED, TRANSFERRED — each names an action or a directed claim, and the direction encodes which way the claim runs. "Entity CONTROLS Wallet" is not the same fact as "Wallet CONTROLS Entity"; one of them is true and one is nonsense, and the ontology should permit only the true one. Beginners often add undirected "related to" edges that mean nothing; a relationship that does not survive the question "in which direction, and meaning what?" should not exist.

**Let the ontology be a contract, not a cage — but a contract first.** There is a real tension between strictness and flexibility. Too strict and you cannot represent facts your data actually contains; too loose and you have no semantics. The resolution in practice is to make the ontology strict about *types and directions* — which is what gives you validation and clean integration — while letting *properties* be open, so a node can carry attributes the ontology did not anticipate. This is exactly the property-graph philosophy, and it is why we chose property graphs for teaching.

## 5. Ingesting and integrating multiple sources

The reason knowledge graphs earn their keep in real systems is **integration**: they let data of different shapes from different providers become one queryable structure. The script ingests two sources of deliberately different shape — a structured CSV transfer ledger and a semi-structured JSON entity directory — and the integration happens almost for free, which is the point.

The mechanism is **identity**. Both sources mention blockchain addresses, and an address *is* a node's identity. So when the CSV mentions `0xALICE` as a transfer recipient and the JSON directory has nothing to say about Alice but the prose later will, the graph does not create two Alices; it creates one node the first time the address is seen and attaches every subsequent fact to that same node. The helper that enforces this is the whole integration story in miniature:

```python
def ensure_address(addr, chain=None):
    if addr not in g:
        ntype = "SmartContract" if addr in contract_addrs else "Wallet"
        g.add_node(addr, type=ntype, label=addr, chain=chain)
```

Notice a subtlety the script handles: it reads the *label feed first* to learn which addresses are contracts, so that when it later encounters those addresses in the transfer ledger it types them correctly as SmartContract rather than Wallet. This is a small instance of a large truth — **the order and priority of your sources is itself a design decision**. When two sources disagree, which wins? Here the directory is authoritative about what an address *is*, and the ledger is authoritative about what *moved*. Naming that priority explicitly, rather than letting it emerge by accident of load order, is part of doing this well.

Contrast this with the relational approach to the same integration. You would have a `transfers` table and a `labels` table, and every question that wants "the transfer *and* who operates the recipient" is a JOIN. Add a third source — say, the prose notes — and you add a third table and another join. The graph instead absorbs each source by mapping it onto the shared ontology and merging on identity, and once absorbed, all sources are queried uniformly. This is why the cross-source question we reach in Part IV — "explain this transfer," answered from three files at once — is trivial in the graph and awkward in SQL.

## 6. Querying: the analytical repertoire

A graph you cannot query is a museum piece. The four queries in `01` are chosen to teach the four shapes of graph question you will use forever, so learn them by shape, not by syntax.

The **one-hop neighbourhood** is the simplest and the one our driving question asks first: given an address, what does it directly touch? In the script this is Q1, and it does something instructive beyond listing neighbours — for each counterparty it looks up the *entity behind* that counterparty, so the answer is not "0xALICE sent to 0xDEX_POOL" but "0xALICE sent to 0xDEX_POOL, which is operated by AquaSwap." That extra hop, from an opaque address to the named operator, is exactly the enrichment a graph makes natural and a flat ledger makes painful.

The **N-hop neighbourhood**, or ego graph, generalises this to "everything within N hops," and it is a single library call:

```python
ego = nx.ego_graph(g.to_undirected(), ADDR, radius=2)
```

This *is* the visual you will put in front of your team — "this address and its two-hop world" — and it is the operation the interactive explorer performs when you type an address and choose a hop count.

**Path-finding between two nodes** answers "how, if at all, are these two things related?" The script asks how Alice relates to Carol and gets back a chain that crosses the DAO treasury and the NFT marketplace — a connection no single transaction reveals and that only emerges from following edges across the graph. The key insight is that the path crosses *heterogeneous relationship types*; the algorithm does not care whether each hop is a transfer or a control link, it just follows edges, which is precisely the capability the relational model lacks without bespoke per-type queries.

**Variable-depth reachability** answers "everything downstream of here, however far." The script traces every address reachable from the DAO treasury along transfer edges, then asks which named entities operate those addresses — combining unbounded traversal with attribute lookup. This is the query family that is genuinely hard in SQL (the recursive CTE with a guessed depth bound) and native in a graph (`nx.descendants`), and it is the one Part III benchmarks.

Beyond these four lie the analytical algorithms that turn a graph from a lookup structure into an instrument of discovery — **centrality** (which nodes are most connected or most influential), **community detection** (which clusters of nodes form natural groups), **shortest weighted paths** (the cheapest route by some edge weight). You do not need them to answer the driving question, but knowing they exist, and that they operate on the same structure with no extra modelling, is part of understanding why the graph is the right home for analysis. A relational schema gives you none of these for free; a graph gives you all of them, because they are defined on exactly the structure the graph already is.

---

# Part III — Why a graph and not an RDBMS, demonstrated

Part I made the argument in prose; `02_kg_vs_rdbms.py` makes it in code, and you should run it and read its output alongside this section, because seeing the recursive CTE next to the one-line traversal does more than any paragraph.

## 7. The same question, two ways

The script loads the identical transfer ledger into a SQLite database and into a NetworkX graph, then asks both: *every address reachable from the DAO treasury, at any depth, with the entity behind each one.*

The SQL answer is a recursive common table expression, and its anatomy is worth studying because its awkwardness is the lesson:

```sql
WITH RECURSIVE reach(addr, depth, path) AS (
    SELECT '0xDAO_TREASURY', 0, '0xDAO_TREASURY'
  UNION
    SELECT t.to_addr, reach.depth + 1, reach.path || ' -> ' || t.to_addr
    FROM transfers t JOIN reach ON t.from_addr = reach.addr
    WHERE reach.depth < 10          -- you must guess a depth bound
)
SELECT DISTINCT reach.addr, reach.depth, l.entity
FROM reach LEFT JOIN labels l ON l.address = reach.addr
WHERE reach.depth > 0;
```

Three things about this query teach the whole point. You had to **write it by hand for this specific question**, and a different question — "everything *upstream*," "only following USDC," "stopping at exchanges" — needs a different hand-written CTE. You had to **guess a depth bound** (`< 10`); too small and you miss deep connections, too large and you waste work, and the *right* bound depends on data you cannot see in advance. And the query exhibits a classic CTE wart visible in the script's output: the same address can appear at multiple depths, because path-carrying recursive CTEs do not deduplicate across the recursion, so `0xALICE` shows up at depth 1 and again at depth 3.

The graph answer is one line, with no depth bound, no hand-written recursion, and no duplication:

```python
nx.descendants(g, "0xDAO_TREASURY")
```

That contrast — a bespoke, bounded, duplicate-prone recursive query versus a single primitive — is the expressiveness argument made concrete.

## 8. The performance shape, honestly

The script then scales up: half a million synthetic transfers across fifty thousand addresses, and a six-hop reachability query run both ways. The graph traversal comes in several times faster than the recursive CTE in memory. But a master reports benchmarks honestly, and the script's commentary does, so absorb the honesty as part of the lesson.

The benchmark **flatters the relational side**. It uses a single relationship type, one table, and an ideal index — the most favourable possible conditions for SQL. The moment you add the other relationship types our real graph contains — CONTROLS, DEPLOYED, OWNS — each hop in the relational world becomes a multi-table join, and the gap widens per relationship type, because the graph traversal still just follows edges regardless of label while the relational query must join across a growing set of tables. Furthermore, this benchmark runs in memory; a disk-backed relational database pays input/output cost per join that a native graph store, exploiting index-free adjacency, largely avoids.

So the performance story is not "graphs are N times faster," a claim that would be brittle and dataset-dependent. The story is that **the relational cost grows with the size of the database and the number of relationship types, while the graph cost grows with the size of the answer**. That is a difference in *shape*, not a constant factor, and it is the difference that decides which model to use as your data and your questions grow. On a thousand-row toy dataset you will not feel it and should not over-engineer; at the scale real on-chain analysis reaches, it is decisive.

Carry away the verdict in its mature form. The graph wins for relationship analysis because traversal is native, depth is unbounded, new relationship types compose without migration, and heterogeneous node types coexist. The relational store wins for bulk storage and aggregation. The competent architecture is hybrid, and choosing the boundary between the two — what lives in SQL, what lives in the graph, how they synchronise — is the senior judgement this tutorial is training you toward.

---

# Part IV — Letting an LLM build the graph

This is the part most people most want and most often get wrong, because they treat the language model as an oracle that emits a finished graph, when the correct design treats it as a *proposer* whose every output is checked by deterministic code. `03_llm_extraction.py` implements the architecture that holds up in production, and understanding *why* it has the shape it has is the heart of mastering this material.

## 9. The four-phase architecture

The pipeline has four phases, and the separation between them is not bureaucratic; each phase exists to contain a specific failure mode of language models.

**Phase one is ontology proposal.** The model reads the corpus and proposes a property-graph ontology — node types, edge types, and their domain and range constraints — and returns it as JSON. A human (or a curated seed ontology) reviews it *once*, and from that moment the ontology is fixed and becomes the contract for everything after. The reason this is a separate phase is that ontology design requires seeing the whole corpus and thinking about types in the abstract, which is a different cognitive task from extracting individual facts; asking the model to do both at once produces muddier results at both.

**Phase two is typed extraction.** The model extracts entity and relationship *instances* that must conform to the phase-one ontology, which is handed back to it in the prompt. Extracting against a fixed schema rather than inventing structure as it goes dramatically reduces a characteristic failure of free-form extraction, where the model coins a slightly different relationship name for the same idea each time it appears — `BOUGHT`, `PURCHASED`, `ACQUIRED` — and you end up with a graph whose edges do not line up. Pinning the ontology first forces consistency.

**Phase three is the validation gate, and it is the phase that separates a toy from a system.** Plain code — not the model — checks every proposed entity and relationship. An entity is rejected if its type is not in the ontology or if it carries no evidence span. A relationship is rejected if either endpoint is missing, if its `(source type, relationship, target type)` triple is not licensed by the ontology, or if it has no evidence span. The slogan to memorise is **the LLM proposes; the validator disposes**. The cached response shipped with the script deliberately contains one wrong-direction triple — an Artwork purchasing a Person — precisely so that when you run the script you watch the gate print `REJECTED` and reject it. That rejection is the single most important line of output in the whole tutorial, because it is the moment the architecture earns your trust.

**Phase four is entity resolution and merge.** The validated entities and relationships are folded into the graph built from the structured sources. The same address or the same canonical name resolves to the same existing node rather than creating a duplicate, so a wallet that appears in the CSV ledger and is described in the prose becomes one enriched node, not two. This is where "multiple sources, one graph" finally pays off across *all three* sources at once.

## 10. Why provenance is non-negotiable

Every entity and every relationship the model extracts must carry an **evidence span** — a short verbatim quotation from the source text that grounds the claim — and the validator rejects anything that lacks one. This requirement does more than it appears to.

Most immediately, it is your defence against hallucination. A language model asked to extract facts will, under some prompts, helpfully *infer* facts that are plausible but not stated, and a knowledge graph silently polluted with plausible inventions is worse than no graph, because it is confidently wrong. Demanding that every fact quote the text that supports it makes invention structurally hard: the model cannot supply a verbatim span for a fact the text does not contain, so the validator can catch fabrications by checking that the claimed evidence actually appears in the source.

It also gives you **auditability**. When the graph asserts that Alice received a grant, you can click that node in the explorer and read the exact sentence from the community notes that the claim rests on. For any serious use — and especially for anything touching money, identity, or compliance — a graph whose every fact traces back to its source is the difference between an analyst's toy and an instrument someone will stake a decision on. Build provenance in from the first line; retrofitting it is painful and usually never happens.

## 11. The cross-source payoff

The script ends on the query that justifies the entire enterprise, and you should run it and sit with the result, because it is the moment the abstract argument becomes a concrete capability you can feel. It asks the graph to *explain the 25,000 USDC transfer to Alice*, and the answer is assembled from three sources that individually know only a fragment:

The CSV ledger knows that 25,000 USDC moved from the treasury address to `0xALICE`. It does not know who that treasury is or why the money moved. The JSON directory knows that the treasury address is operated by Lighthouse DAO. It knows nothing about the transfer or about Alice. The prose notes know that Alice owns that wallet and that the DAO approved a grant to her — the *why* — and carry the verbatim sentence as evidence. No single source can explain the transfer. The graph, having merged all three on identity, explains it in one traversal, with the reasoning grounded in a quotation you can verify.

That is the thing to demonstrate to your team, because it is the thing a relational schema makes laborious and a knowledge graph makes native: **questions whose answers live across the seams between your data sources**. The graph dissolves the seams.

## 12. Prompt design and failure modes

A few hard-won practices, so that when you adapt this to your own corpus you avoid the common traps.

Demand **strict JSON with no prose and no markdown fences**, and parse defensively, stripping fences if they appear anyway. Models drift toward conversational wrapping; the prompts in the script say "respond with ONLY a JSON object" for that reason, and the parser strips ```` ```json ```` defensively because belt and braces costs nothing.

Hand the model the **ontology verbatim** in the extraction prompt and instruct it to use only the types defined there. This is what turns the ontology from a suggestion into a constraint, and combined with the validation gate it gives you two independent lines of defence — the model is *asked* to conform, and the code *checks* that it did.

Expect and design for **the model proposing too many types**. Left unguided, a model will often mint more node and edge types than the domain needs, splitting near-synonyms. The instruction to "prefer reusing a general type over inventing near-duplicates" pushes back, and the human review step in phase one is your chance to consolidate before the ontology hardens.

Treat **entity resolution as the hard part it is**. The script resolves on exact address or exact label match, which is the clearest baseline for teaching, but real corpora say "Alice," "Alice Chen," "@alice_dev," and "0xALICE" for the same person, and matching them requires alias tables, fuzzy string matching, or embedding similarity. When your graph has mysterious duplicate nodes, the cause is almost always resolution that was too strict; when it has wrongly merged distinct things, resolution that was too loose. This is where you will spend real engineering effort, and knowing that in advance is itself part of mastery.

---

# Part V — Visualisation and interactive exploration

A knowledge graph is one of the rare data structures where a good visualisation is not a luxury but a genuine analytical tool, because the eye finds clusters, bridges, and outliers that no query you thought to write would have surfaced. `04_visualize.py` emits a single self-contained HTML file — no server, no build step — and you open it in a browser.

## 13. What makes a graph visualisation useful rather than pretty

The default instinct is to draw every node and edge and call it done, which on any real graph produces an unreadable hairball. Three design decisions separate a useful explorer from a decorative one, and the script embodies all three.

The first is **focus on demand**. The explorer's headline feature is the one you asked for directly: type an address, choose a hop depth, and the explorer performs a breadth-first traversal from that node across *all* relationship types and highlights exactly the neighbourhood within that many hops, fading everything else. This is the visual form of the ego-graph query from Part II, and it is the right default interaction because it matches the driving question — given an address, show me its world — and because it tames the hairball by showing only the part the analyst is asking about. The traversal is a dozen lines of JavaScript and worth reading, because it is the same BFS you met in Python, now driving a layout:

```javascript
function neighbourhood(start, depth){
  const dist = {[start]: 0}, q = [start];
  while(q.length){
    const c = q.shift();
    if(dist[c] >= depth) continue;
    for(const nx of adj[c]) if(!(nx in dist)){ dist[nx] = dist[c]+1; q.push(nx); }
  }
  // fade everything not in dist; highlight edges within the neighbourhood
}
```

The second is **type as colour, and filtering by type**. Each node type gets a colour, and chips let you hide whole types at once, so you can strip the graph down to, say, only people and organisations and see the social layer without the transaction noise. This directly exploits the heterogeneity that justified the graph: because types are first-class, the visualisation can reason about them, which a flat diagram cannot.

The third is **provenance on inspection**. Click any node and a panel shows its properties, and for nodes the LLM extracted from prose it shows the verbatim evidence span and a marker indicating the source. This closes the loop opened in Part IV: the analyst is never asked to trust a fact, they can read the sentence it came from. A visualisation that surfaces provenance turns the explorer from a picture into an argument.

The layout itself is a **force-directed simulation**: edges act as springs pulling connected nodes together, nodes repel each other, and the system settles into an arrangement where structure becomes visible — tightly connected clusters draw together, bridging nodes sit between them, isolated nodes drift to the edge. You do not position anything by hand; the physics reveals the topology. This is why force layouts dominate graph visualisation, and why the same dataset that is an inscrutable adjacency list as text becomes legible as a force-directed picture.

## 14. The demo, and why it lands

Put the explorer in front of your team and do this. Type `0xALICE`, set hops to two, and show the neighbourhood light up — the DAO that funded her, the exchange she withdrew to, the pool she traded in, all reachable in two steps. Then click the `Alice` person node, which exists *only* because the LLM read it out of prose, and show the evidence span: the sentence from the community notes that grounds her existence in the graph. Then toggle the type filters to hide transfers and reveal the pure relationship layer — who is a member of what, who created what, who pays fees to whom. In ninety seconds you will have shown ingestion from three sources, LLM-driven construction, provenance, heterogeneity, and the answer to the driving question, all in one moving picture. That is the payoff the whole pipeline was built to deliver.

---

# Part VI — Production and the road to mastery

You now understand the ideas and have run them end to end at teaching scale. Mastery is the bridge from there to systems that hold real load, and this part maps that bridge and gives you a way to keep climbing.

## 15. From NetworkX to a real graph engine

NetworkX is a superb teaching and prototyping tool and an in-memory library, which means it is bounded by your RAM and offers no persistence, concurrency, or transactional guarantees. The production step is a dedicated graph engine, and there are two families matching the two traditions from Part I.

The **labelled-property-graph** family — Neo4j and Memgraph foremost — stores nodes and edges with properties, persists to disk, exploits index-free adjacency at scale, and is queried in **Cypher**, a language whose pattern syntax reads like the graph it matches. Our driving question, "everything within two hops of an address," becomes a single readable clause:

```cypher
MATCH (a:Wallet {address: '0xALICE'})-[*1..2]-(neighbour)
RETURN a, neighbour
```

That `[*1..2]` is variable-depth traversal as a first-class language construct — the thing that was a hand-written recursive CTE in SQL is a few characters in Cypher — and seeing it is the clearest possible confirmation of the expressiveness argument from Part III. The four-phase LLM architecture from Part IV ports unchanged; only the final merge step writes to Neo4j instead of NetworkX.

The **RDF** family — triple stores like GraphDB, Blazegraph, or Amazon Neptune — stores everything as subject-predicate-object triples, expresses ontologies in **RDFS** and **OWL**, validates instance data with **SHACL** (which generalises the hand-rolled validation gate into a declarative constraint language), queries in **SPARQL**, and uniquely supports **inference**: an OWL reasoner can derive new facts your data did not state but logically entails, such as concluding that two wallets owned by the same person are linked even where no edge says so directly. Choose this family when formal semantics, interoperability across organisations, or logical inference matter; choose the property-graph family when developer ergonomics and raw traversal performance matter. Knowing the trade-off, rather than defaulting to whichever you met first, is a mark of mastery.

## 16. Hardening the pipeline

Several things that were simplified for teaching become real engineering in production, and naming them tells you where the work lives.

**Entity resolution** graduates from exact matching to a genuine subsystem — alias tables, fuzzy matching, blocking strategies to avoid comparing every node with every other, and increasingly embedding-based similarity for the hard cases. This is usually the largest single source of graph-quality problems and deserves proportionate investment.

**Ingestion** moves from reading static files to streaming from live sources — for on-chain data, a node's RPC interface, an indexer, or a warehouse export from a service like Dune or BigQuery — and the pipeline must handle updates, retractions, and the fact that sources disagree and change. The ontology-mapping and merge logic you built stays the same; what changes is that it now runs continuously over a moving target.

**The LLM stage** acquires cost and latency budgets, caching (the script's cached response is a primitive version of this), batching, and monitoring of extraction quality over time, because a model that quietly starts proposing different ontologies as your corpus drifts will corrupt the graph slowly and invisibly without it.

**The hybrid boundary** from Part III becomes concrete infrastructure: a relational or columnar store of record for the raw ledger and aggregations, the graph for analysis, and a synchronisation pipeline keeping them consistent. Designing that boundary well — deciding what is authoritative where, and how staleness is bounded — is the architectural judgement everything in this tutorial has been preparing you to exercise.

## 17. Exercises

Understanding is confirmed by building, so work these in order; each extends the scripts you have and forces a concept into your hands.

**Exercise one, warm-up.** Add a new node type, `Validator`, and a new edge type, `(Person, STAKES_WITH, Validator)`, to the hand-built ontology in `01`. Add a few staking rows to the CSV and a corresponding mapping, and confirm the validator accepts the new edges and rejects a deliberately wrong one such as `(Token, STAKES_WITH, Validator)`. This cements the domain-and-range mechanism.

**Exercise two, querying.** Write a new query in `01` that answers "which two addresses are the most connected" using a centrality measure (NetworkX provides `degree_centrality` and `betweenness_centrality` out of the box). Then ask the same question of the SQLite version in `02` and feel the difference; centrality has no natural relational expression.

**Exercise three, the RDBMS boundary.** Extend `02` so the recursive CTE also returns the *path* to each reachable address and observe the duplication problem first-hand, then write the graph version that returns paths without duplication using `nx.all_simple_paths`. Articulate in one paragraph why the CTE duplicates and the traversal does not.

**Exercise four, LLM extraction.** Write a second prose document describing a *new* part of the ecosystem — a lending protocol, say, with depositors and borrowers — and run it through `03`. Watch the LLM propose new types for concepts the first ontology never saw, and decide by hand which to accept, which to merge into existing types, and which to reject. This is ontology governance, the judgement that does not automate.

**Exercise five, the hard one.** Introduce an entity-resolution challenge: have the prose refer to a person by name only ("Alice") with no wallet address in the same sentence, and a separate sentence that links the name to the address. Modify the resolution logic so the two facts merge onto one node. When you have done this, you have met the central difficulty of real knowledge-graph construction.

**Exercise six, production.** Stand up Neo4j locally (the Docker image is a single command), port the final merge step of `03` to write to it via the Python driver, and rewrite the four queries from `01` in Cypher. Experiencing `[*1..2]` traversal in a real engine is the moment the expressiveness argument stops being theoretical.

## 18. A roadmap to mastery

Mastery here is not a single skill but a stack of them, and you climb it roughly in this order. First, fluency with the **three layers** — ontology, entities, relationships — until separating them is automatic and you spot, in any messy real-world dataset, what the types and relationships ought to be. Second, **ontology design judgement**: the taste to choose general types over near-duplicates, to make relationships directed and meaningful, and to set the strictness dial correctly for the use case. Third, **the integration craft** — identity, resolution, source priority, and the discipline of provenance — which is where most real effort goes and most real value is created. Fourth, **the model-fit judgement** that lets you decide, for a given question at a given scale, whether the graph, the relational store, or a hybrid is right, and to defend the choice with the cost-shape argument rather than fashion. Fifth, **the LLM architecture** — proposer-and-validator, provenance-grounded, with the gate doing the work the model cannot be trusted to do alone. And finally, the **production engineering** that makes all of it durable: a real engine, a real ingestion pipeline, a real resolution subsystem, and a well-drawn boundary between the graph and the systems around it.

Internalise one closing mental model, because it organises everything above. A relational database answers questions about *rows*; a knowledge graph answers questions about *paths*. The art is recognising, in any problem in front of you, which kind of question it really is — and the blockchain address with which we began is, unmistakably, a question about paths. When you can see that clearly, instantly, in problems you have never met before, you have mastered this.

---

## Appendix — the four scripts at a glance

```
01_manual_kg.py      Hand-built ontology, two-source ingest, four query shapes.
                     Read this to understand WHAT a knowledge graph is.

02_kg_vs_rdbms.py    The same questions in SQLite and in a graph, plus a
                     scale benchmark. Read this to understand WHY a graph.

03_llm_extraction.py The four-phase LLM pipeline: propose ontology, extract,
                     validate, merge. Read this to understand how the graph
                     BUILDS ITSELF from unstructured text.

04_visualize.py      A self-contained interactive explorer with address search
                     and hop control. Read this to understand how to SEE it.
```

Run them in order, read the part of this tutorial that pairs with each, do the exercises, and you will not merely have followed a recipe — you will own the ideas.
