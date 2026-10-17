# Numerical study: reproduction, field audit and limits

17 October 2026. Assistant-completed research for Aroosh; human/team review pending. This is an offline descriptive analysis, **not agent performance or causal strategy evidence**.

Inputs: [Kaggle publisher](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games), [saved publisher metadata](../../../research/metadata/kaggle-lumins.json), [Chabot's article](https://duddhawork.com/blog/catan-analytics-how-to-win-with-data-driven-strategies/). Dataset contributor Lumin and article author Olivier Chabot are different people. Raw CSV SHA-256: `5d8d31fa9623391e659f275d12c8facacf202924624fd509a1c5c6abd939b6e0`; unchanged, not uploaded.

## Data dictionary by original position

Positions below are **zero based**, preventing automatic duplicate-header renaming. The JSON retains every original header separately.

| Position | Original header | Meaning / uncertainty | Available to an opening decision? |
|---|---|---|---|
| 0 | gameNum | Game group, 1–50 | Grouping ID only; no predictive meaning |
| 1 | player | Publisher-documented starting position 1–4 | Seat descriptor, but four-player only |
| 2 | points | Final points; >=10 defines winner | **No: outcome** |
| 3 | me | Publisher describes contributor's position; actual cells are 1 or empty, one flag per game | Identity confound; do not encode as a general strategy feature |
| 4–14 | 2,3,...,12 | End-game dice histogram, repeated identically for all four players | **No: realized future luck** |
| 15,17,19 | settlement1, blank, blank | First settlement's three number entries | Initial board descriptor after placement; not all available before choices |
| 16,18,20 | blank, blank, blank | Their paired resource/port/desert tokens | Same |
| 21,23,25 | settlement2, blank, blank | Second settlement's number entries | Same; chosen placements are outcomes of opening decisions |
| 22,24,26 | blank, blank, blank | Their paired tokens | Same |
| 27 | production | Total settlement/city cards gained | **No: post-game; no per-resource breakdown** |
| 28 | tradeGain | Cards gained in peer **and** bank trades | **No; trade types inseparable** |
| 29 | robberCardsGain | Robber/non-Knight dev gains; Road Building valued as four resource equivalents by publisher | **No; not a robber-only field** |
| 30 | totalGain | 27+28+29 | **No** |
| 31 | tradeLoss | Peer and bank trade cards given | **No** |
| 32 | robberCardsLoss | Robber/Knight/opposing Monopoly losses | **No** |
| 33 | tribute | Discards when seven rolled | **No** |
| 34 | totalLoss | 31+32+33 | **No** |
| 35 | totalAvailable | 30−34 | **No** |

Resource tokens verified by publisher: L wood, C brick/clay, S sheep, W wheat, O ore. `3G` is general port; `2X` is a resource port; D desert. There are **two undocumented B tokens**, both with number 0. Do not reinterpret B as brick: C already means brick. The primary analysis excludes those two player records **only from complete-case settlement descriptors**. Placement, roll and quality checks retain all 200 rows. Descriptor denominators are 198 players / 49 winners; not 200 / 50.

All six pair slots are inspected per record: 1,152 ordinary productive pairs, 46 documented zero-number port/desert pairs and two unresolved pairs. Pips are `min(n−1,13−n)` for productive numbers 2–12 other than seven. Coverage counts productive resource types, never a port as a producing resource. Known pips across all records average 20.005; complete-case average is 20.0354. No missing token is silently imputed.

## Quality and dependence

- 200 rows, 36 columns, 50 groups of four distinct seats. IDs span 1–50. Zero duplicate records or game/seat keys. One >=10-point winner in every game. No numeric-data empty cells; `me` has 150 empty cells consistent with its observed flag pattern. Blank headers are structural, not missing observations.
- All three derived gain/loss identities hold in all 200 records. Dice histograms agree within each game, so game length counts one histogram, not four.
- `me=1` occurs once per group: 50 flagged records, 25 wins; 150 unflagged records, 25 wins. Interpreting the flag as contributor identity fits the metadata but remains an interpretation of its encoding. This imbalance is strong evidence to account for player selection/skill, not to attribute all differences to placement or resources. Seat-specific flag counts are in the JSON.
- There are **50 game groups**, not 200 independent observations. Repeated contributor, unrecorded opponents and an uncontrolled personal sample further limit independence/representativeness.

## Reproduced claims versus new descriptors

| Calculation | Result | Status / denominator |
|---|---|---|
| Seat-order wins | 8,18,14,10 → 16%,36%,28%,20% | **Reproduced** article table; 50 games per seat, one winner each |
| Total dice rolls per game | Mean 64.28; sample SD 12.7408; range 38–99 | **Reproduced** rounded article mean 64 / SD 13; n=50 |
| Mean starting pips | Known productive pairs: 20.005 | Consistent with article's rounded 20; unknown B pairs retained as unresolved |
| Resource diversity 2 / 3 / 4 / 5 | 0/1, 5/27, 27/105, 17/65 wins | **New complete-case descriptors**, not a byte-for-byte reproduction of the article's chart or a significance test |
| Wheat access present / absent | 47/178 vs 2/20 wins | **New complete-case descriptors**. Absent group is exactly 10%; does not reproduce the article's “less than 10%” statement under this exclusion policy |
| Winner / nonwinner initial pips | 20.7959 / 19.7852 | Descriptive, n=49 /149 in complete cases; within-game dependent |
| Contributor's four-variable best-subsets model | Claimed 40/50 games | **Not reproduced**: exact variables, fitting specification and independent validation not established |
| City/dev versus roads outcome claim | Not identifiable from these columns | No purchase counts, building trajectories or per-resource realized totals. Do not invent proxies as original variables |

The script outputs all five resource presence denominators. These small, selected associations cannot establish that ignoring brick/wood is good in 1v1. A winner may collect more because early building increased production; realized totals can be consequences of success. Missing board topology, ports over time, opponents and build history block many stronger explanations.

Seat Wilson intervals in JSON are **nominal illustrations under independent-game assumptions**: roughly 8.3–28.5%, 24.1–49.9%, 17.5–41.7%, 11.2–33.0%. They are not causal effects, simultaneous intervals or calibrated predictions for two players. Resource subgroups get no naive independent-row confidence claims. A later exploratory model would require game-grouped splits/resampling, decision-time inputs and an explicit model-selection disclosure; none was fitted.

The article's luck calculation uses final dice counts; even if reproduced, it is retrospective. We did not reconstruct its luck bins or infer unrecorded resource-specific collection/build variables. This deliberately bounds what has been reproduced.

## Reproduce and verify

```bash
./team-work/run-python.sh team-work/member-1/phase-1/audit_csv.py \
  research/downloads/datasets/catanstats.csv \
  > team-work/member-1/phase-1/csv-audit.json
```

Read [script](audit_csv.py) and [actual aggregate output](csv-audit.json). Primary verification independently recomputed group histograms, winners, dice means/SD and raw token inventories before comparing script output. No dataset rows, model or game were generated. Dataset license metadata says CC BY-NC-SA 4.0; attribution/source links are retained and raw records remain local. See [economic hypotheses](02-ECONOMY-AND-HYPOTHESES.md).
