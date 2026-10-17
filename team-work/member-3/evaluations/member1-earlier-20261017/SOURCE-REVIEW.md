# Primary source review: Member 1 earlier bots

This inventory was independently read and checked by the primary assistant. Hyde timed out and supplied no accepted output. Code fingerprints in `source-inventory.json` define exactly which uploaded files are evaluated; no bot was rewritten.

| Original filename | Implemented approach | Static evaluation | Main CPU controls |
| --- | --- | --- | --- |
| `agent.py` | UCT tree search; configured truncated random rollout depth **1**; one/two sampled worlds depending on action count | `base_fn(DEFAULT_WEIGHTS)` divided by 1e8; explicit terminal reward | Adaptive cost estimate; 10/30 ms ceiling; at most 30% of remaining credit; static priority below search floor |
| `agent_claude.py` | Similar UCT search with rollout depth **6** | Same base function and scale, explicit terminal reward | Same 10/30 ms ceilings and 30% fraction |
| `agent_claude_greedy_v2.py` | One-world one-ply scan; optional top-four same-turn follow-up | Default base function; no explicit terminal override in scoring | 40 ms budget cap and 12% fraction; root scan can exceed this budget before stopping |
| `agent_claude_greedy_v3.py` | One-world one-ply greedy scan; optional opponent-value subtraction | Default weights in this evaluation, `OPP=0`; CONTENDER option not tested | No internal deadline; official external clock remains active |
| `agent_claude_greedy_v4.py` | Relative one-ply scan; top-three contested candidates can receive greedy own follow-ups plus a bounded worst opponent reply | `V(me) - V(opponent)`; separate terminal handling in refinement | Root 12/60 ms and 30% fraction; refinement 40/120 ms and 20% fraction after reserve |
| `agent_modifiedf.py` | One-world one-ply scan using a hand-written feature-dictionary score and geometry | Public VP, own/enemy production, frontier, hand synergy, dev/army/road terms; own hidden VP term | Adaptive candidate estimate; 12/45 ms ceilings and 30% fraction |
| `agent_sab.py` | Same-turn depth-two maximizing refinement of top four; no alternating opponent search | Default base function /1e8; explicit terminal reward | Predicts root/refinement cost, 11/30 ms ceiling and 30% fraction; static priority if root estimate cannot fit |

## Findings independent of win rate

1. **Source comments are not measurements.** Claims about earlier baselines, exact replay, guaranteed complete root scans or guaranteed F quality were not accepted as benchmark evidence. Deadline-controlled scans can end early. Adaptive timing means a fixed random seed does not guarantee identical work across runs/hardware.
2. **Top-level exceptions are hidden from harness error counts.** Every candidate catches exceptions and can return `rng.randrange(...)`. `internal-fallback-sites.json` records the seven exact return lines. A returned legal index is a successful decision to the harness even when the strategy failed. Separate diagnostics will report observed occurrences; zero occurrences over a small diagnostic does not rule them out elsewhere.
3. **MCTS comments differ from configured depth.** `agent.py` actually sets `ROLLOUT_DEPTH=1`; `agent_claude.py` sets 6. The distinction is retained in results. Random simulated chance is a sampled possibility, not knowledge of real future dice or hidden cards.
4. **SAB may skip expensive opening evaluation.** In `_decide`, the root estimate is `n * _est_leaf_s * SAFETY`, initially `n * .0008 * 1.25`, while the wide ceiling is .030 s. At more than 30 actions, its initial guard selects a static-priority move rather than examining the full root. This is a code-derived condition, not an established cause of a particular game loss. Despite its name, this same-turn maximizer is not a general alternating alpha-beta opponent search.
5. **Greedy v4 has bounded horizons.** `_two_ply` can hit the own-follow-step limit before the turn ends, and caps own/opponent action scans. It is not an exhaustive minimax or uniform end-of-turn comparison. Relative scoring uses a sampled opponent hand, not real hidden opponent information.
6. **Modified F is untrained.** It uses a manually weighted `create_sample` dictionary plus engine geometry; dataset availability does not make this a learned evaluator. Its own hidden-VP weight is 1e8 versus 3e14 for public VP; an own VP is not weighted equally across those two terms. That is a design observation, not proof of a bug or the reason for any loss.

## Scope

Only default uploaded versions are evaluated. No optional weight sweep, training, code fixes, B01/B02 reassignment, other member implementation, portal action or SSH. Recommendations are review instructions for Aroosh, not implemented changes.
