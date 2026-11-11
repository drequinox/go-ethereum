"""flowsim - bounded adversarial exploration of message-sequence flows.

Model a flow as actors exchanging messages. The engine explores every
interleaving (delivery order = reordering) plus a bounded network adversary
(drop, duplicate, replay, tamper) and optional actor compromise (forge).
Safety invariants are checked in every reachable state, terminal invariants
at quiescence. Breadth-first search gives the shortest counterexample.

Bounded: no counterexample within the bounds is evidence, not proof.
Escalate critical invariants to TLA+/TLC or Tamarin/ProVerif.

Usage:
  python3 flowsim.py MODEL.py [--budget drop=1,dup=1,replay=1,tamper=1,forge=1]
                              [--compromised A,B] [--sweep K]
                              [--max-states N] [--max-depth D] [--out DIR]
MODEL.py must define MODEL = <instance of a Model subclass>.
Requires Python 3.8+ and the standard library only.
"""
import argparse, copy, hashlib, importlib.util, itertools, json, os, sys
from collections import deque, Counter


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), default=str)


def H(*parts):
    return hashlib.sha256(canon(parts).encode()).hexdigest()[:16]


def sign(signer, payload):
    """Abstract unforgeable signature: only producible by code acting as signer."""
    return {"signer": signer, "mac": H("SIG", signer, payload)}


def verify(sig, signer, payload):
    return isinstance(sig, dict) and sig.get("signer") == signer and sig.get("mac") == H("SIG", signer, payload)


class Reject(Exception):
    """Raise in a handler when the receiver refuses a message."""


def msg(mid, src, dst, kind, **body):
    return {"id": mid, "src": src, "dst": dst, "kind": kind, "body": body}


class Model:
    name = "model"
    actors = []
    messages = []      # every declared message id, for coverage
    # channels[(src, dst)] = {"authenticated": bool, "replay_protected": bool}
    #   authenticated:    network adversary cannot alter the message in transit
    #   replay_protected: network adversary cannot duplicate or replay it
    # Anything not stated in the documents defaults to False (insecure).
    channels = {}
    invariants = {}    # name -> fn(state) -> bool, checked in every state
    terminal = {}      # name -> fn(state) -> bool, checked at quiescence
    tamper = {}        # kind -> [(label, fn(body) -> body)]

    def initial(self):
        raise NotImplementedError  # -> (state dict, [messages])

    def handle(self, s, m, send):
        fn = getattr(self, "on_%s_%s" % (m["dst"], m["kind"]), None)
        if fn is None:
            raise Reject("no handler for %s.%s" % (m["dst"], m["kind"]))
        fn(s, m, send)

    def forge(self, actor, s):
        return []      # messages an attacker controlling `actor` can emit


def _chan(model, m):
    return model.channels.get((m["src"], m["dst"]), {})


def _can_tamper(model, m, compromised):
    if m["src"] in compromised or m["dst"] in compromised:
        return True
    return not _chan(model, m).get("authenticated", False)


def _can_replay(model, m, compromised):
    if m["src"] in compromised or m["dst"] in compromised:
        return True
    return not _chan(model, m).get("replay_protected", False)


def explore(model, budget=None, compromised=(), max_states=200000, max_depth=40):
    budget = dict({"drop": 1, "dup": 1, "replay": 1, "tamper": 1, "forge": 1}, **(budget or {}))
    compromised = frozenset(compromised)
    s0, inflight0 = model.initial()
    root = (canon(s0), tuple(sorted(canon(m) for m in inflight0)), frozenset(), tuple(sorted(budget.items())))
    parent = {root: None}
    depth = {root: 0}
    q = deque([root])
    violations, coverage, rejects = {}, Counter(), Counter()
    flags = {"depth_limited": False}
    states = 0

    def record(node, name, kind):
        if name in violations:
            return
        trace = []
        n = node
        while parent[n] is not None:
            p, ev = parent[n]
            trace.append(ev)
            n = p
        violations[name] = {"kind": kind, "trace": list(reversed(trace)), "state": json.loads(node[0])}

    def check(node):
        s = json.loads(node[0])
        for name, f in model.invariants.items():
            if not f(s):
                record(node, name, "safety")

    def push(node, prev, ev):
        if node in parent:
            return
        parent[node] = (prev, ev)
        depth[node] = depth[prev] + 1
        check(node)
        if depth[node] < max_depth:
            q.append(node)
        else:
            flags["depth_limited"] = True

    check(root)

    while q and states < max_states:
        node = q.popleft()
        states += 1
        sj, inflight, delivered, b = node
        bud = dict(b)
        s = json.loads(sj)
        if not inflight:
            for name, f in model.terminal.items():
                if not f(s):
                    record(node, name, "terminal")
        moves = []
        for i, mj in enumerate(inflight):
            rest = inflight[:i] + inflight[i + 1:]
            m = json.loads(mj)
            moves.append(("deliver", m, rest))
            if bud["drop"]:
                moves.append(("drop", m, rest))
            if bud["dup"] and _can_replay(model, m, compromised):
                moves.append(("dup", m, inflight))
            if bud["tamper"] and _can_tamper(model, m, compromised):
                for label, fn in model.tamper.get(m["kind"], []):
                    moves.append(("tamper", m, rest, label, fn))
        if bud["replay"]:
            for mj in delivered:
                m = json.loads(mj)
                if _can_replay(model, m, compromised):
                    moves.append(("replay", m, inflight))
        if bud["forge"]:
            for a in sorted(compromised):
                for fm in model.forge(a, copy.deepcopy(s)):
                    moves.append(("forge", fm, inflight, a))

        for mv in moves:
            op, m = mv[0], mv[1]
            nb = dict(bud)
            if op == "deliver":
                s2 = copy.deepcopy(s)
                out = []
                send = lambda mid, src, dst, kind, **body: out.append(msg(mid, src, dst, kind, **body))
                try:
                    model.handle(s2, m, send)
                    coverage[m["id"]] += 1
                    ev = {"op": "deliver", "msg": m}
                except Reject as r:
                    s2, out = s, []
                    rejects[(m["id"], str(r))] += 1
                    ev = {"op": "reject", "msg": m, "reason": str(r)}
                nin = tuple(sorted(mv[2] + tuple(canon(o) for o in out)))
                nd = delivered | {canon(m)}
                push((canon(s2), nin, nd, tuple(sorted(nb.items()))), node, ev)
            elif op == "drop":
                nb["drop"] -= 1
                push((sj, mv[2], delivered, tuple(sorted(nb.items()))), node, {"op": "drop", "msg": m})
            elif op in ("dup", "replay"):
                nb[op] -= 1
                nin = tuple(sorted(mv[2] + (canon(m),)))
                push((sj, nin, delivered, tuple(sorted(nb.items()))), node, {"op": op, "msg": m})
            elif op == "tamper":
                nb["tamper"] -= 1
                tm = dict(m, body=mv[4](copy.deepcopy(m["body"])))
                nin = tuple(sorted(mv[2] + (canon(tm),)))
                push((sj, nin, delivered, tuple(sorted(nb.items()))), node,
                     {"op": "tamper", "msg": tm, "label": mv[3]})
            elif op == "forge":
                nb["forge"] -= 1
                nin = tuple(sorted(mv[2] + (canon(m),)))
                push((sj, nin, delivered, tuple(sorted(nb.items()))), node,
                     {"op": "forge", "msg": m, "actor": mv[3]})

    exhausted = not q
    return {
        "model": model.name,
        "compromised": sorted(compromised),
        "budget": budget,
        "states": states,
        "exhausted": exhausted,
        "depth_limited": flags["depth_limited"],
        "complete": exhausted and not flags["depth_limited"],
        "violations": violations,
        "coverage": {mid: coverage.get(mid, 0) for mid in model.messages},
        "uncovered": [mid for mid in model.messages if not coverage.get(mid)],
        "rejects": [{"msg": k[0], "reason": k[1], "count": v} for k, v in rejects.items()],
    }


def compromise_sweep(model, max_k=2, **kw):
    """Explore with every actor subset up to size max_k compromised.
    Returns (minimal compromise sets per invariant, True if every run was complete)."""
    hits, complete = {}, True
    for k in range(0, max_k + 1):
        for subset in itertools.combinations(model.actors, k):
            r = explore(model, compromised=subset, **kw)
            complete = complete and r["complete"]
            for inv in r["violations"]:
                hits.setdefault(inv, []).append(frozenset(subset))
    minimal = {}
    for inv, sets in hits.items():
        mins = [s for s in sets if not any(o < s for o in sets)]
        minimal[inv] = sorted(sorted(s) for s in set(mins))
    for inv in list(model.invariants) + list(model.terminal):
        minimal.setdefault(inv, [])
    return minimal, complete


def _lbl(t):
    return str(t).replace(";", ",").replace("#", "no.").replace("\n", " ")


def trace_to_mermaid(model, name, v, title=None):
    lines = ["sequenceDiagram"]
    if title:
        lines.insert(0, "%% " + _lbl(title))
    lines.append("  participant ADV as Adversary")
    for a in model.actors:
        lines.append("  participant %s" % a)
    for ev in v["trace"]:
        m = ev["msg"]
        tag = _lbl("%s %s" % (m["id"], m["kind"]))
        if ev["op"] == "deliver":
            lines.append("  %s->>%s: %s" % (m["src"], m["dst"], tag))
        elif ev["op"] == "reject":
            lines.append("  %s->>%s: %s" % (m["src"], m["dst"], tag))
            lines.append("  Note over %s: rejected - %s" % (m["dst"], _lbl(ev["reason"])))
        elif ev["op"] == "drop":
            lines.append("  %s-x%s: %s DROPPED" % (m["src"], m["dst"], tag))
        elif ev["op"] in ("dup", "replay"):
            lines.append("  Note over ADV: %s %s" % (ev["op"], tag))
        elif ev["op"] == "tamper":
            lines.append("  Note over ADV: tamper %s - %s" % (tag, _lbl(ev["label"])))
        elif ev["op"] == "forge":
            lines.append("  Note over ADV: forge as %s - %s" % (ev["actor"], tag))
    a0, a1 = model.actors[0], model.actors[-1]
    lines += ["  rect rgb(255,220,220)", "  Note over %s,%s: VIOLATED %s" % (a0, a1, _lbl(name)), "  end"]
    return "\n".join(lines) + "\n"


def _load(path):
    spec = importlib.util.spec_from_file_location("flowmodel", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MODEL


def main():
    ap = argparse.ArgumentParser(description="Bounded adversarial exploration of a flow model.")
    ap.add_argument("model")
    ap.add_argument("--budget", default="", help="e.g. drop=1,dup=1,replay=1,tamper=1,forge=1")
    ap.add_argument("--compromised", default="", help="comma-separated actors compromised in the main run")
    ap.add_argument("--sweep", type=int, default=-1, help="also sweep all actor subsets up to this size")
    ap.add_argument("--max-states", type=int, default=200000)
    ap.add_argument("--max-depth", type=int, default=40)
    ap.add_argument("--out", default="sim_out")
    a = ap.parse_args()
    model = _load(a.model)
    budget = {k: int(v) for k, v in (p.split("=") for p in a.budget.split(",") if p)}
    comp = [c for c in a.compromised.split(",") if c]
    unknown = [c for c in comp if c not in model.actors]
    if unknown:
        sys.exit("unknown actor(s): %s; actors are %s" % (unknown, model.actors))
    os.makedirs(a.out, exist_ok=True)
    kw = dict(budget=budget, max_states=a.max_states, max_depth=a.max_depth)

    r = explore(model, compromised=comp, **kw)
    print("[%s] states=%d complete=%s compromised=%s budget=%s"
          % (model.name, r["states"], r["complete"], r["compromised"], r["budget"]))
    if not r["complete"]:
        print("  WARNING: search hit a bound (states or depth); results are partial")
    for name, v in r["violations"].items():
        fn = os.path.join(a.out, "cx-" + "".join(c if c.isalnum() else "_" for c in name)[:40] + ".mmd")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(trace_to_mermaid(model, name, v, title="%s: %s" % (model.name, name)))
        print("  VIOLATION %s (%s) in %d steps -> %s" % (name, v["kind"], len(v["trace"]), fn))
    if not r["violations"]:
        print("  no violations within bounds")
    print("  uncovered messages: %s" % (r["uncovered"] or "none"))
    for rj in r["rejects"]:
        print("  reject %s: %s (x%d)" % (rj["msg"], rj["reason"], rj["count"]))
    out = {"run": r}
    if a.sweep >= 0:
        ms, complete = compromise_sweep(model, max_k=a.sweep, **kw)
        out["minimal_compromise_sets"] = ms
        out["sweep_complete"] = complete
        print("  minimal compromise sets (k<=%d, complete=%s):" % (a.sweep, complete))
        for inv, sets in ms.items():
            print("    %s: %s" % (inv, sets if sets else "none found"))
    with open(os.path.join(a.out, "results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    sys.modules["flowsim"] = sys.modules["__main__"]  # models import the same Reject/sign objects
    main()
