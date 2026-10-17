# Member builds → uploads → assistant verification → improvement rounds

17 October 2026. This is the user's requested future workflow, specified without implementing a runner, bot, fixture or tournament. See the [eight-bot assignment](../../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md).

## Ownership and the repeatable loop

1. **Each human owner builds two separate bots** in their own member folder, reusing the existing environment. Keep bot code changes confined to the owner's branch/folder. Two configurations of the same bot are not automatically two distinct strategies: document the decision differences.
2. **Owner tests first.** Verify loading, legal integer indices, exact phase semantics, lack of runtime network/workers, artifact paths and a bounded smoke/profile run under the unchanged harness. Then run paired comparisons versus frozen F and the owner's other bot as resources permit. Keep errors and exhausted-clock games. A smoke win is not a strength claim.
3. **Owner uploads code, manifest and evidence to GitHub**, with a frozen commit, exact entrypoint, commands, results and known issues. No environment, token, dependency tree or raw dataset. A member branch can be uploaded without immediately merging shared files. Supply repository access through the team's normal GitHub process; no collaborator invitations were sent here.
4. **Owners/user supply the uploaded round here.** The existing authorization covers assistant review and feedback. The assistant retrieves the exact versions, inspects code and dependencies, checks local/remote hashes, repeats essential tests, verifies claimed results and runs controlled comparisons. A claimed pass is not accepted without actual evidence. No fabricated O opponent.
5. **Assistant returns concrete improvement tickets to owners in Markdown**, linked to evidence. Each ticket records bot/version, failing behavior or weak matchup, source/seed/fixture evidence, likely cause, proposed change, acceptance test, CPU risk and priority. This means feedback here/in the repository; it does not authorize messaging people or another chat automatically.
6. **Owners improve and upload new versions**, including rejected ideas and what changed. The assistant verifies again and compares with the frozen parent plus peers on fresh development batches. Repeat while time and evidence justify changes. Do not silently replace old artifacts or erase losses.
7. **Freeze candidates and package.** Keep eight working local strategy candidates if all qualify; repeated rounds may produce more variants. Eight strong finalists require evidence, not merely eight folders. Select event submissions from the strongest dependable artifacts under the actual remaining upload allowance.

The assistant owns independent cross-bot verification and synthesis after uploads; each member owns their own implementation, self-tests and fixes. Anni builds two bots too: she is not assigned everyone else's testing infrastructure. Pranesh likewise builds his own two bots; the assistant does not take that implementation over in this task.

## Required upload packet per bot

Proposed directory: `team-work/member-N/bots/Bxx/v001/`, containing an entrypoint and only its necessary files. Add a sibling Markdown report/JSON manifest with:

- Bot ID/version/parent, strategy and distinguishing decisions, human builder and independent assistant review status.
- Frozen Git commit, entrypoint, source/config/data/weight SHA-256 and kit/engine revisions. If learned later, label provenance and all splits become mandatory.
- Exact commands, working directory, interpreter/library versions, hardware and load conditions. Reference the common environment, never copy it.
- Seed batch IDs/ranges, board/seat pairing, game indices/order, dice-key identifier, opponents and their hashes, process boundaries and adaptation state policy.
- Per-game harness output plus summary: wins/games, no-winner losses, own CPU mean/p95/max, exhausted-clock games, random fallback moves, errors, timeouts, crashes and initial load time. A p95 is computed from records, not invented from the mean.
- Fault examples, known limitations, semantic checks, change versus parent, rejected experiments and requested review questions.

`match.play_chunk` already returns game index, board seed, first-seat flag, winner, turns and each seat's CPU/wall/decision/over/fallback/error/timeout/crash fields; its second return contains initial load times. `evaluate.run` returns an aggregate, **not the per-game records**. A future owner/assistant wrapper must preserve the returned records. No wrapper was built here.

Artifact hashes/configs, machine details, peak memory, explanatory decisions, policy-cache/adaptation settings, round identity and evidence locations need extra logging. Do not claim stock harness fields contain them. Memory checks must use permitted external monitoring without charging a bot for the monitor; scorer enforcement remains authoritative.

## Eligibility before interpreting wins

Use exact-rules 10 VP, unchanged kit/engine/clock, one thread per numeric library. A candidate must load within the official limit, return a genuine in-range integer and complete under its cumulative clock. Target zero faults and exhausted-clock games; any such event triggers investigation before advancement. Keep a tested cheap legal fallback inside the bot; harness random fallback is a recorded failure mode, not the intended policy.

Do not patch the harness, predict private dice from boards, treat sampled hidden identities as observed, import unlisted packages or include compiled binaries in submissions. New tactical fixtures must reach/construct explicitly valid phases and assert transitions; source-level Road cut and masked-terminal risks are still unproven runtime cases. A plausible comment is not a fixture result.

For local timing, run matches sequentially on an otherwise quiet laptop first. Record own process CPU, not elapsed whole-game wall time. Later parallel development across members/machines is allowed, but concurrent laptop results cannot substitute for a controlled profile. Reserve budget for observation/serialization and fallback; choose search limits only after measurements. Local timing does not certify the scorer.

## Proposed staged game budget — not executed

Counts below are planning defaults, not power guarantees. Reduce scope by dropping weak variants and optional comparisons, not by relabeling smoke tests as validation.

| Stage | Proposed comparisons | Games | Interpretation |
|---|---|---:|---|
| Owner smoke/profile | 4–20 per bot plus semantic checks | 32–160 total for eight | Catch errors and clock faults only |
| Broad screen | Eight candidates ×40 versus F; all 28 candidate pairings ×20 | 880 | Very uncertain triage; keep full matrix, avoid a knockout-only verdict |
| Larger comparison | Provisional top four ×400 versus F; six pairings ×200 | 2,800 | Resolve promising alternatives, include a retained stylistic counterbot if the screen suggests cycles |
| Submission shortlist confirmation | Top two ×1,000 versus F; their pairing ×400 | 2,400 | Confirm frozen artifacts; O/private event strength still unknown |
| Optional eight-finalist evidence | Eight ×1,000 versus F; 28 pairings ×200 | 13,600 | Only if measured capacity permits; counts are a separate full batch, not free reuse of selection data |

The three main stages total **6,080 games**, excluding smoke, parent ablations, repeats and optional eight-finalist evidence. Each improvement round adds new eligibility work and comparisons. A full round robin of B candidates uses `B*(B−1)/2` matchups. Do not run a giant matrix for every weight variant.

At measured sequential throughput `t` seconds/game, a batch costs roughly `G*t` plus load/logging/review overhead. For 6,080 games, 1 s/game implies about 101 minutes; 3 s/game about 304 minutes. These are arithmetic scenarios, **not observed throughput**. Measure a small batch first, budget all machines separately, and cut optional work before consuming packaging time. The pinned statement closes uploads at 17:00 IST and reports at 17:30 on 17 October; the portal teammate checks operative timing/remaining slots. This protocol does not assume an extension or untouched submission allowance.

## Splits, uncertainty and selection

Use disjoint board-seed groups for development, selection and confirmation. Seats of one board stay in the same group. Register batches before seeing outcomes; assign distinct namespaces to rounds and roles and retain their lists locally/with results. Repeated development uses fresh development groups and frozen parents; it never consumes a reserved confirmation batch casually. If confirmation is used to rank or modify bots, disclose selection and obtain a new final batch before claiming an untouched test.

Start with **no cross-game opponent learning** for the first comparison round. Fix process lifecycle, game order, RNG/cache behavior and all opponent versions. A persistent owned RNG can make a single isolated replay differ; preserve full ordered batches and separately check boundary handling. If adaptive variants are later allowed, compare multiple independently reset process batches with declared order and treat batch-level dependence explicitly; a naive per-board bootstrap is then insufficient.

For a fixed, nonadaptive candidate versus one opponent, record pair score `(win_in_seat1 + win_in_seat2)/2`. Each no-winner is zero for both bots; do not turn it into half a win or drop it. Report mean, board-pair count, seat results, no-winners and operational counters. Use board-pair clustered resampling for descriptive intervals under independence assumptions, not the CLI's independent-game normal interval. At degenerate 0/100% or tiny samples, do not report a zero-width bootstrap/normal interval as certainty: a bounded-score Hoeffding interval with half-width `sqrt(log(2/alpha)/(2*n_pairs))`, clipped to [0,1], is a conservative alternative **if independent board-pair assumptions hold**. For paired candidate differences on identical board groups, resample pair differences together; their range is [-1,1], so the corresponding Hoeffding half-width is `sqrt(2*log(2/alpha)/n_pairs)`.

These bounds follow the bounded-independent-variable inequality associated with [Hoeffding (1963), publisher record](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500830); the full publisher text was inaccessible during this task. Their application here is a proposed methodological calculation, not a tested statistical package. Multiple candidates/comparisons and repeated selection make unadjusted intervals optimistic. Prefer predeclared comparisons and final confirmation; if claiming simultaneous coverage, declare the comparison family and adjust alpha. Do not decide solely from overlapping intervals or a single aggregate win rate. Preserve the entire matchup matrix: A can beat B, B beat C and C beat A.

Selection proceeds in order: operational eligibility; F-anchor evidence; broad peer strength; weakest-matchup behavior; uncertainty; complexity/maintenance cost. When uncertain, retain the simpler parent or collect more preallocated games rather than announce a winner. Internal weak-matchup performance is a proxy; official robustness uses five weakest of nine group opponents and cannot be computed from this local set.

## Upload and improvement ledger

The initial registry is B01–B08 in the shared plan. First submitted versions are `v001`; do not call them finalists before evidence exists. Each next version points to its parent and the improvement ticket it addresses. Compare one interpretable change where practical. If one failed case is fixed but a weak matchup worsens, keep both results and explain the tradeoff.

Official limits remain **seven scored submissions / ten total uploads**, including failures. Eight bots are a local development portfolio, not permission for eight scored event submissions. The user/team chooses what to send through the portal teammate's existing process. This task only publishes research/plans to GitHub and takes no SSH or event-portal action.
