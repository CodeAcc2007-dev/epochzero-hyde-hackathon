# B05 upgrade handoff — second-highest shared-board F result

17 October 2026. User explicitly requested that a teammate improve B05 while the primary session improves B01. This task is **B05 only**, even if you are another numbered member. Preserve B01 and every other bot. No SSH, event submission, secrets, copied environment or runtime LLM.

## Exact starting point

- Standalone baseline: [B05 v004 agent.py](bots/B05/v004/agent.py).
- SHA256: `8226e2c978cd6ec48fee2939dd4ccf021acb64e131b87bc71ddfcd29e0d05cbf`.
- [Manifest](bots/B05/v004/manifest.json), [single-file ZIP](artifacts/B05-v004.zip).
- [500 saved game records](implementation/round-2/main/B05-v004-new-vs-F-500/games.json), [summary](implementation/round-2/main/B05-v004-new-vs-F-500/summary.json), [metadata](implementation/round-2/main/B05-v004-new-vs-F-500/metadata.json).
- Result **375/500 =75.0%**, mean own CPU167.68ms/game, maximum790ms; zero recorded errors/timeouts/crashes/clock overruns/random harness moves. Boards934000–934249, swapped seats, process reset every20 games. These boards are used evidence.
- B01 v002 scored390/500 on the same boards. This is an observed F ordering, not proof of direct head-to-head strength or event performance. B05's previous matched v003 had371/500; improvement was not established (reset-chunk difference interval includes zero).

The standalone file is the authoritative complete implementation. The manifest's component hashes are provenance, not runtime dependencies. Earlier v003 source/tests are already in the repository. Do not accidentally start from v003 just because an older AGENTS.md section names it.

## Work order

1. Read root AGENTS.md, setup notes, this brief, the standalone v004 and its results. Verify SHA before editing. Reuse shared-local with `./team-work/run-python.sh`; if working on another computer, follow02-LOCAL-SETUP-AND-VALIDATION.md for one local installation. No SSH; do not commit environment or downloaded datasets.
2. Create a separate branch `member-3/b05-final-upgrade` and a new version v005 if unused. Preserve v004 bytes and evidence. Record your plan in Markdown before experiments. Do not merge main automatically.
3. Inspect reached mistakes first. Prioritize economical search improvements: preserve promising trade/road enablers, choose useful completions before greedy pruning, avoid spending the beam on equivalent states, improve known near-terminal sequences. Current B05 has width5, depth4,80 expansions and22ms per-decision soft cap. Do not simply enlarge all limits. Existing v004 already adds 3 greedy + up to2 useful enabler slots and a bounded immediate terminal selector; do not reimplement these as a new contribution.
4. Test one or two interpretable variants. Other hypotheses: balanced opening resource access, useful city/settlement production and timing, Knight/Army readiness. Keep hidden-card expectations distinct from guaranteed wins. Use only the observation/public fields and own known hand; never actual hidden opponent identities, deck order, future dice or board-seed lookup.
5. Preserve original action indices, observation immutability, exact bank/port/piece constraints, new-card and one-dev-per-turn rules, strict Road/Army holder thresholds and engine simultaneous-winner behavior. Guaranteed wins must precede fallback and chance-valued buys. No broad exception swallowing.
6. Add targeted regressions that demonstrate the intended change. Use existing test fixtures as support, adapting them to the exact standalone candidate. Verify both player seats, low clock, bank depletion, original root ordering and terminal cases. Distinguish constructed states from reached game histories.
7. Use bounded development games, then freeze before main confirmation. Main: **500 games per new bot**, paired seats, unchanged F, original cumulative clock min(.300+.0125*decisions,1.500)s, process reset every20 games. Use fresh boards **941000–941249** for candidate and matched v004 parent, reserved for this teammate; B01 uses938000/939000. Do not reuse confirmation boards for tuning. Reuse existing run_comparison.py. If time cannot cover matched parent, disclose that and avoid a matched improvement claim.
8. Record all outcomes, fault/CPU counts, source and F hashes, commands, seed range, lifecycle, hardware, rejected variants and uncertainty. A worse variant is a rejected experiment, not a reason to edit results. If no candidate improves reliably, recommend v004 and deliver experiments separately.
9. Deliver one standalone agent.py and ZIP containing exactly agent.py, plus README, manifest and evidence. Verify ZIP bytes equal the tested file. No sibling runtime modules, model calls, environment or secrets. Commit only B05 scope and your evidence, push your branch if credentials are available, and give the user file links and exact commit. Do not submit to the event or merge another person's work.

If Hyde GLM is available, use it for bounded mechanical work through team-work/run-hyde-junior.py; primary reasoning/review still belongs to the acting engineer. If you are GLM yourself, follow the same constraints and verification discipline; do not block on a second model.

## Evaluation command template

Run from repository root; substitute a new evidence folder that does not exist. Repeat for the preserved v004 parent using the same seed range/lifecycle. Never overwrite an existing output.

```bash
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py --a team-work/member-3/bots/B05/v005/agent.py --b shared-local/organizer-kit/examples/f_agent.py --games 500 --seed0 941000 --chunk-size 20 --out team-work/member-3/evaluations/B05-v005-final-vs-F-500
```

F SHA256 must be `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613`; kit04fffac90e00610f60e0b06d919f262f4b3ed9db; engine d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816. Do not edit F, engine or clock.
