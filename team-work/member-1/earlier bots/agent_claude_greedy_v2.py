import random
import time
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

VALUE_FN = base_fn(DEFAULT_WEIGHTS)
VP_UNIT = 1e13          # raw value units; one public VP is 3e14, so this is well below a VP
TOPK = 4
MAX_FRACTION = 0.12     # share of remaining allowance one decision may use
HARD_MAX_S = 0.040
MIN_LEFT_S = 0.004

class Agent:
    def __init__(self):
        self.rng = random.Random(0)

    def decide(self, obs, acts):
        try:
            return self._decide(obs, acts)
        except Exception:
            return self.rng.randrange(len(acts))

    def _decide(self, obs, acts):
        n = len(acts)
        if n <= 1:
            return 0
        t_start = time.process_time()
        left = obs.cpu_left if obs.cpu_left is not None else 0.010
        budget = min(HARD_MAX_S, MAX_FRACTION * max(left, 0.0))
        deadline = t_start + budget
        me = obs.me
        world = obs.sample_world(self.rng)

        scored = []                      # (value, index, child_game)
        for i in range(n):
            try:
                g = world.copy()
                g.execute(world.playable_actions[i], validate_action=False)
            except Exception:
                continue
            scored.append((VALUE_FN(g, me), i, g))
            # Never stop mid-pass unless we are truly out of credit: F's baseline always runs.
            if time.process_time() - t_start > max(budget, 0.003) * 3:
                break
        if not scored:
            return self.rng.randrange(n)
        scored.sort(key=lambda t: -t[0])
        best_v, best_i, _ = scored[0]
        if len(scored) == 1 or time.process_time() >= deadline:
            return best_i

        # Lookahead only over candidates that F's one-ply cannot separate by a VP-sized margin.
        cands = [t for t in scored[:TOPK] if best_v - t[0] < VP_UNIT * 30]
        if len(cands) < 2:
            return best_i
        final = {}
        for v, i, g in cands:
            if time.process_time() >= deadline:
                break
            if g.winning_color() is not None or g.state.current_color() != me:
                final[i] = v
                continue
            sub = g.playable_actions
            bv = v
            for j in range(len(sub)):
                if time.process_time() >= deadline:
                    break
                try:
                    g2 = g.copy()
                    g2.execute(sub[j], validate_action=False)
                except Exception:
                    continue
                v2 = VALUE_FN(g2, me)
                if v2 > bv:
                    bv = v2
            final[i] = bv
        if not final:
            return best_i
        return max(final, key=lambda k: (final[k], -k))
