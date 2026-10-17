import os, random, time
from catanatron.players.value import DEFAULT_WEIGHTS, CONTENDER_WEIGHTS, base_fn
W = CONTENDER_WEIGHTS if os.environ.get("W") == "contender" else DEFAULT_WEIGHTS
V = base_fn(W)
OPP = float(os.environ.get("OPP", "0"))   # weight on opponent's own value (zero-sum-ness)

class Agent:
    def __init__(self): self.rng = random.Random(0)
    def decide(self, obs, acts):
        try:
            w0 = obs.sample_world(self.rng)
            me = obs.me
            opp = [c for c in w0.state.colors if c != me][0]
            best = None; bv = None
            for i, a in enumerate(acts):
                g = w0.copy(); g.execute(a, validate_action=False)
                v = V(g, me)
                if OPP: v -= OPP * V(g, opp)
                if bv is None or v > bv: bv, best = v, i
            return best
        except Exception:
            return self.rng.randrange(len(acts))