# Verification record and review questions

Scope: **Pranesh, Member 3, Phase 1**. This task inspected source/literature, checked arithmetic and wrote documents. No engine state was constructed, fixture executed, agent implemented, new data generated, policy trained or match played.

## Primary-assistant verification

1. Read the working agreement and Member 3/common brief; the initial worktree was clean.
2. Read action generation/application, resource/VP helpers, turn cleanup, board routes and terminal loops. Traced kit observation/masking, harness and the two kit patches. Installed engine provenance names the required commit.
3. Hashed eleven installed source files and compared them with exact-commit raw/API content or local organizer Git objects. [source-verification.json](source-verification.json) records each method. Failed raw requests were resolved by successful alternate checks, not called verified by assumption.
4. Visually inspected Guhe–Lascarides physical PDF p4 (planning/measurement) and Deep Catan physical PDF p3 (rules/player setting), with extracted text and primary hosted versions. Did not reproduce experiments or review all paper results.
5. Independently checked resource/VP ledgers and phase conditions. Example building compositions leave the stated pieces available. Board geometry remains assumed, not an executed fixture.
6. Read Hyde's complete arithmetic draft before execution. Imports were limited to `fractions`, `json`, `math`; no engine, network, file or dynamic execution calls. Added normalization/nonnegative assertions.
7. Ran the reviewed script using the existing shared Python. Five checks passed; [derivations.json](derivations.json) is its actual output. No catanatron import or `Game` call exists.
8. Checked the written claims against original sources and retained uncertainty labels. The final handoff is a draft awaiting user/cross-member review.

## Hyde jobs and senior disposition

| Job | Actual result | Disposition |
|---|---|---|
| `20261017T062414Z-c05b8ae4`: core source table | Output, zero tool errors; 182.060 seconds | **Used selectively with corrections.** Retained claims checked against source; missing reset dependency located independently. Raw table not copied wholesale. |
| `20261017T062547Z-35a0fa86`: VP/road/hidden table | Timed out at 240.159 seconds, exit 130; no output | **Rejected/no result.** No retry loop; senior completed the source analysis. |
| `20261017T062652Z-5f32a5fa`: arithmetic script | Output, zero tool errors; 147.269 seconds | **Accepted with edits and independent execution.** Senior read all operations, added checks, then ran it. |

All used `hyde-inference/hyde/glm-5.3-flash`. Inputs were selected numbered source excerpts or a mathematical specification. No GitHub PAT, `.env`, environment tree or unrelated teammate work was supplied. Local manifests retain hashes, events, time and reported usage; raw reasoning/session logs are not included in the shareable research pack.

### Corrections to the extracted table

- It counted 17 dispatch appliers while its list sums to 18. The irrelevant count was not propagated.
- It described some prompts as unchanged although the appliers explicitly set `PLAY_TURN`. The audit states behavior in the required phase/call context.
- Its packet lacked the reset helper. The senior located `player_clean_turn` L338–354; that packet limit did not imply a missing engine reset. Cumulative played counts remain; per-turn/eligibility flags change.
- Missing helper details were checked directly where needed. Model assertions were not accepted as proof.

## Reproduce the arithmetic checks

From the project root:

```bash
./team-work/run-python.sh team-work/member-3/phase-1/verify_derivations.py
git -C shared-local/organizer-kit status --short
git -C shared-local/organizer-kit rev-parse HEAD
```

The five checks cover trade/city resources and VP, road/settlement resources, Army arithmetic/relative swing, discard quotas, and an exchangeable-card toy probability. They do not prove board reachability, legality or strategic superiority. Those semantics were inspected in source with the limits recorded in the audit.

Source comparison initially hit SSL/transport failures on raw HTTPS requests. Successful fallback methods were GitHub contents API comparison or a local exact-commit organizer Git object. No source/dependency was changed to pass a check.

## Limits that must survive later planning

- No claim of beating F/O, fitting the clock, optimality or empirical robustness.
- R1 is a missing-guard source path, not a demonstrated reachable exploit or runtime reproduction.
- R2's bound follows from the real nonterminal harness loop; artificial/terminal states need separate handling. A sample does not reveal the opponent's hand.
- The toy hypergeometric fractions are not dataset statistics or calibrated opponent-win probabilities.
- No new full-corpus tactical audit; the existing dataset catalogue's limits remain.
- During the research task, no teammate review was received and no message, SSH/portal action or publication occurred. Pranesh subsequently authorized GitHub publication of this draft on 17 October 2026; user and Avadooth review remain pending.

## Questions for Pranesh's verification

1. **Terminal timing:** the harness checks after a complete action, before requesting its next follow-up; `Game.execute` does not terminate midway. Is Case B's explanation clear?
2. **Case preconditions:** the examples assume legal nodes/edges and available pieces. Which should become exact map fixtures later?
3. **Road risk:** require cut/tie fixtures before relying on a Road-denial strategy; no engine changes in this phase.
4. **Hidden VP:** accept `H≤9−p` for real ongoing play while retaining history/selection uncertainty; do not interpret toy fractions as measured threat rates.
5. **Candidate isolation:** H1 phase/terminal, H2 completion chains and H3 threats/bonuses should remain separately testable until evidence supports combining them.

Your verification and Avadooth's cross-review remain **pending**. Stop here before implementing the next phase.
