"""Model template: F1 withdrawal signing with a human approver.

Copy, rename, and replace the handlers with ONLY the checks the documents state.
FIX levels show the before/after pattern for proposed remediations.

Self-test (expected results):
  FIX=0  violates S1 (unauthenticated request tampered; approver approves what is shown)
         and S4 (sign order replayed)
  FIX=1  S1 holds, S4 still violated
  FIX=2  no violation within bounds; Policy and Signer are each a single-actor compromise set
  FIX=2 REPLAY_PROTECTED=1  same as FIX=2 (shows the channel option)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flowsim import Model, Reject, sign, verify, H

FIX = int(os.environ.get("FIX", "0"))
RP = os.environ.get("REPLAY_PROTECTED") == "1"
INTENT = {"to": "client-wallet", "amt": 50, "chain": 1}   # ground truth: what the client asked for


class WithdrawalFlow(Model):
    name = "F1 withdrawal fix-level %d" % FIX
    actors = ["Initiator", "Policy", "Approver", "Signer", "Chain"]
    messages = ["F1.M1", "F1.M2", "F1.M3", "F1.M4", "F1.M5"]
    channels = {
        ("Initiator", "Policy"): {"authenticated": False},                       # UNSPECIFIED -> insecure default
        ("Policy", "Approver"): {"authenticated": True},
        ("Approver", "Policy"): {"authenticated": True},
        ("Policy", "Signer"): {"authenticated": True, "replay_protected": RP},   # True only if documented
        ("Signer", "Chain"): {"authenticated": True},
    }
    tamper = {"TxRequest": [("redirect to attacker", lambda b: {**b, "tx": {**b["tx"], "to": "attacker"}})]}
    invariants = {
        "S1 executed tx equals client intent": lambda s: all(t == INTENT for t in s["Chain"]["executed"]),
        "S4 one approval, one execution": lambda s: len(s["Chain"]["executed"]) <= 1,
    }

    def initial(self):
        s = {"Initiator": {}, "Policy": {"pending": {}}, "Approver": {}, "Signer": {"signed": []},
             "Chain": {"executed": []}}
        return s, [{"id": "F1.M1", "src": "Initiator", "dst": "Policy", "kind": "TxRequest", "body": {"tx": INTENT}}]

    def on_Policy_TxRequest(self, s, m, send):
        tx = m["body"]["tx"]
        s["Policy"]["pending"][H(tx)] = tx
        send("F1.M2", "Policy", "Approver", "ApprovalPrompt", tx=tx, h=H(tx))

    def on_Approver_ApprovalPrompt(self, s, m, send):
        tx = m["body"]["tx"]
        # Human step. As documented, the approver approves whatever is displayed.
        # FIX>=1: the approver checks the display against an out-of-band client instruction.
        if FIX >= 1 and tx != INTENT:
            raise Reject("displayed tx does not match client instruction")
        send("F1.M3", "Approver", "Policy", "Approve", h=m["body"]["h"], sig=sign("Approver", m["body"]["h"]))

    def on_Policy_Approve(self, s, m, send):
        h = m["body"]["h"]
        if not verify(m["body"].get("sig"), "Approver", h):
            raise Reject("approver signature invalid")
        if h not in s["Policy"]["pending"]:
            raise Reject("unknown tx hash")
        tx = s["Policy"]["pending"][h]
        send("F1.M4", "Policy", "Signer", "SignOrder", tx=tx, att=sign("Policy", tx))

    def on_Signer_SignOrder(self, s, m, send):
        tx = m["body"]["tx"]
        if not verify(m["body"].get("att"), "Policy", tx):
            raise Reject("policy attestation invalid")
        if FIX >= 2:
            if H(tx) in s["Signer"]["signed"]:
                raise Reject("already signed")
            s["Signer"]["signed"].append(H(tx))
        send("F1.M5", "Signer", "Chain", "SignedTx", tx=tx, sig=sign("Signer", tx))

    def on_Chain_SignedTx(self, s, m, send):
        tx = m["body"]["tx"]
        if not verify(m["body"].get("sig"), "Signer", tx):
            raise Reject("bad signature")
        if FIX >= 2 and tx in s["Chain"]["executed"]:
            raise Reject("nonce already used")
        s["Chain"]["executed"].append(tx)

    def forge(self, actor, s):
        bad = {"to": "attacker", "amt": 50, "chain": 1}
        if actor == "Initiator":
            return [{"id": "F1.M1", "src": "Initiator", "dst": "Policy", "kind": "TxRequest", "body": {"tx": bad}}]
        if actor == "Policy":
            return [{"id": "F1.M4", "src": "Policy", "dst": "Signer", "kind": "SignOrder",
                     "body": {"tx": bad, "att": sign("Policy", bad)}}]
        if actor == "Signer":
            return [{"id": "F1.M5", "src": "Signer", "dst": "Chain", "kind": "SignedTx",
                     "body": {"tx": bad, "sig": sign("Signer", bad)}}]
        return []


MODEL = WithdrawalFlow()
