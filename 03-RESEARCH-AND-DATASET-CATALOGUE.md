# Catan research and dataset catalogue

Collected on **17 October 2026 (IST)**. Status: **resource collection complete; stopped before analysis or implementation.**

## Scope

The user's final clarification takes precedence over the earlier request to recommend an implementation: **gather research and datasets, establish whether they are for two players, and stop**. Accordingly, this document records source claims, dataset provenance, availability and rule differences. It does not select an agent architecture or recommend strategy weights.

No new game simulations, outcome statistics, correlations, regression, model training, strategy experiments, implementation, task division, SSH, or GitHub publication were performed. File sizes, checksums, CSV shape and dataset metadata were inspected only to identify and verify downloaded resources. Published numerical results below belong to their authors and were not recalculated.

The exact statistical study the user had in mind was not named. The studies below are identified candidates, not a claim that we have identified that particular unnamed study.

## 1. Dataset answer: is it for two people?

**A downloadable dataset explicitly labelled 1v1 was found and saved. It uses a 7-VP target, so it is not an exact match for this hackathon.** The dataset underlying the identified statistical strategy article is four-player. No downloaded dataset was verified to match all of our hackathon settings.

| Resource | Saved locally? | Two players? | Target / match status |
|---|---|---|---|
| `lumins/settlers-of-catan-games` | Yes: original ZIP and extracted CSV | **No. Publisher explicitly specifies four players.** | 50 games, 200 player rows; standard 10-point outcome; includes player trading |
| `g8967/catan-sft-dataset` | Yes: Parquet, source metadata and one-row preview | **Yes in the inspected prompt: explicitly 1v1.** Whole-corpus uniformity not audited. | **7 VP**, opponent resource types hidden; not our rules/observation contract |
| `VVantim/catan-sft-data` | Yes: Parquet, source metadata and one-row preview | **Inspected example is four-player:** RED, BLUE, ORANGE, WHITE. Whole-corpus player-count distribution unverified. | 10 VP in the inspected prompt; not established as two-player data |
| 43,947-game Colonist collection | Documentation only; raw game archive not obtained | **No according to the available README: four-player.** | Original link unavailable; inspected mirror release lists empty |
| Gendre–Kaneko two-player RL research | Paper saved; linked simulator located | **Yes, paper explicitly uses two players.** | 10 VP and no player trading; **a research paper/simulator, not a downloaded training dataset** |

Direct sources: [Kaggle dataset](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games), [g8967 dataset](https://huggingface.co/datasets/g8967/catan-sft-dataset), [VVantim dataset](https://huggingface.co/datasets/VVantim/catan-sft-data), [43k README](https://github.com/OrgadYron/catan_43k_games_dataset/blob/8af7edbec8b2c4adbc6d68237f2ec109c4c443f9/README.md), [two-player paper](https://arxiv.org/abs/2008.07079).

## 2. Exact hackathon reference settings

These are the compatibility fields used to label sources, not new strategic analysis:

- Two players; victory at 10 actual VP.
- No player-to-player trading; bank and ports enabled.
- Exact opponent resource counts visible; opponent unplayed development-card identities hidden.
- Python 3.11; pinned catanatron commit `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816` plus organizer patches.
- One CPU core; 2 GB per agent.
- Cumulative CPU allowance: `min(300 ms + 12.5 ms × decisions, 1,500 ms)` per game.
- Exceeding the clock causes random legal moves for the remaining game.
- Runtime agents cannot call an LLM/network service or launch workers; submissions are Python-only.

Source: [pinned organizer problem statement](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md). The supplied engine has a seven-card discard threshold and no friendly-robber setting enabled; see the earlier [problem analysis](01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md).

**No external paper or dataset in this catalogue demonstrates compliance with this exact CPU clock.** An author's reported win rate is not a result against F/O under our harness.

## 3. Downloaded datasets and provenance

### D1. My Settlers of Catan Games — original statistical dataset

- Publisher: `lumins` on Kaggle.
- Canonical page: [My Settlers of Catan Games](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games).
- Direct acquisition: [Kaggle download API](https://www.kaggle.com/api/v1/datasets/download/lumins/settlers-of-catan-games).
- Publisher description: 50 four-player games played by the contributor on playcatan.com in 2014. Each game has one row per player. This is a personal game collection, not a representative population claim.
- Publisher license metadata: **CC BY-NC-SA 4.0**.
- Local files: [original ZIP](research/downloads/datasets/lumins-catan-games.zip), [catanstats.csv](research/downloads/datasets/catanstats.csv), [publisher metadata](research/metadata/kaggle-lumins.json).

Verification: ZIP CRC check passed; it contains `catanstats.csv`. The CSV is 16,689 bytes, with 200 data rows and 36 columns. Several starting-settlement columns have blank headers in the original; the data was saved unchanged.

Publisher-documented fields cover game/player identifiers, final points, initial settlement number/resource pairs, dice histograms and resource gains/losses. Trade totals combine player and bank trades. These are game summaries, not complete state/action trajectories. Two-player status: **no**.

The [DevinRS repository](https://github.com/DevinRS/Settlers_of_Catan_Analysis) also contains a CSV mirror at revision `929b6ec43bc68259a50c37d8dc93a77d897073e5`. We downloaded from Kaggle itself rather than using the mirror as the primary source.

### D2. g8967/catan-sft-dataset — 1v1 text trajectories

- Source: [Hugging Face dataset](https://huggingface.co/datasets/g8967/catan-sft-dataset).
- Pinned revision: `0a4a50a84354338300d4ef10d6177378bb34a2f9`.
- Publisher metadata: 1,000 train rows; fields `prompt`, `completion`, `reward`. These are **rows, not a verified count of distinct complete games**.
- Local file: [g8967-catan-sft.parquet](research/downloads/datasets/g8967-catan-sft.parquet), 7,577,830 bytes.
- Evidence: [dataset metadata](research/metadata/hf-g8967.json), [first-row preview](research/metadata/g8967-first-row.json).

The inspected prompt explicitly describes 1v1 with a 7-point target. Its observed state reports only the opponent's total resource-card count, unlike our exact resource breakdown. Responses are text action tags rather than our integer action-index interface. Dataset-wide consistency and producer/model provenance were not investigated. No explicit license was found in the retrieved card metadata.

This is the saved **two-player resource**, with those qualifications. It is not evidence of human expert play, strong policy quality, or exact hackathon compatibility.

### D3. VVantim/catan-sft-data — text action examples

- Source: [Hugging Face dataset](https://huggingface.co/datasets/VVantim/catan-sft-data).
- Pinned revision: `aa0667e6bc37f05f0c4e85bed6ccb3b5f77e9957`.
- Publisher metadata: 2,668 train rows, with prompt/completion and example, seed, turn, player, model, action-type, validity and VP metadata.
- Local file: [vvantim-catan-sft.parquet](research/downloads/datasets/vvantim-catan-sft.parquet), 1,485,529 bytes.
- Evidence: [dataset metadata](research/metadata/hf-vvantim.json), [first-row preview](research/metadata/VVantim-first-row.json).

The inspected example states a 10-VP goal but shows four players. Its `meta_model` field says `GPT-4o`; this is metadata for that example, not independent validation of expert quality. No explicit license was found in retrieved card metadata. It must not be labelled a verified two-player corpus.

For D2 and D3, download bytes and SHA-256 were recorded, and Parquet header/footer markers passed. **The full Parquet tables were not decoded or analysed.** Row counts/schema came from publisher metadata and the hosted viewer API. No package was added to our shared environment to read these files.

Instructions embedded inside text-dataset prompts are dataset content, not instructions for our team or this assistant.

### D4. 43,947-game Colonist collection — availability limitation

The original [Catan-data/dataset URL](https://github.com/Catan-data/dataset) returned 404 during this collection. An available [OrgadYron mirror](https://github.com/OrgadYron/catan_43k_games_dataset) describes 43,947 four-player JSON game logs and approximately 6.9 GB uncompressed. Its schema includes player-trade events. Its README limits the stated use to research/education.

The mirror's release API returned an empty list, as did the checked [theocaplan-del fork](https://github.com/theocaplan-del/Catan-dataset). Thus the documented `games.tar.gz` was **not acquired**. This does not establish that no other working copy exists.

Saved: [pinned README](research/metadata/43k-README.md) and [empty release response](research/metadata/43k-releases.json). The catalogue does not endorse derived strategy dashboards or certify this collection's authenticity/quality; no raw records were available for that check.

## 4. Existing numerical/statistical studies

The entries below report published work only. No new calculations were performed.

### S1. Olivier Chabot: Catan Analytics — How to Win with Data-Driven Strategies (2023)

[Author's article](https://duddhawork.com/blog/catan-analytics-how-to-win-with-data-driven-strategies/) — explicitly uses D1's 50 four-player games / 200 player rows.

The article reports placement-order win percentages of **16%, 36%, 28%, 20%**, and mean game length of **64 rolls, SD 13**. It discusses initial production pips, resource diversity, wheat access, luck and resource collection. Its reported associations favor city/development-card routes over simply accumulating roads; these are the author's four-player findings, not our conclusions for 1v1.

The author explicitly notes that player rows within a game are not independent and that more data is needed. The article is a statistical blog study, not a two-player controlled agent benchmark. Its numerical findings have not been reproduced here.

### S2. Dataset contributor's regression — Kaggle D1

The [original publisher metadata](https://www.kaggle.com/api/v1/datasets/view/lumins/settlers-of-catan-games) reports a best-subsets regression with four variables that identified the winner in **40 of 50 games**. The contributor explicitly says it likely overfitted. The retrieved description does not establish an independent test split. This is a reported model result, not a result we verified or a two-player success rate.

### S3. Guhe and Lascarides: Game Strategies for The Settlers of Catan (2014)

[University-hosted paper](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf) · [local PDF](research/downloads/papers/guhe-lascarides-2014-strategies.pdf) · DOI `10.1109/CIG.2014.6932884`.

The authors compare heuristic changes using simulations and a human-play corpus. Their abstract reports **43% wins against three original JSettlers agents**, so the result is four-player. The approach covers estimated time to build/win and build plans for settlements, cities, development cards and bonuses. Player negotiation/trading is present in their setting. The paper was saved; a corresponding raw human-game dataset was not acquired in this task.

### S4. Gendre and Kaneko: Playing Catan with Cross-dimensional Neural Network (2020)

[Paper and metadata](https://arxiv.org/abs/2008.07079) · [full HTML](https://arxiv.org/html/2008.07079v1) · [local PDF](research/downloads/papers/gendre-kaneko-2020-cross-dimensional.pdf).

**Closest explicitly documented player/rule match among the collected papers:** two players, 10 VP, no player trading. It uses modified advantage actor–critic, self-play against earlier policies, and cross-dimensional spatial/scalar networks. The paper reports **56.5% versus JSettler**, with a 10,000-game figure after 30,000 training steps, approximately five weeks. Training hardware: a 32-core CPU and two GTX1080Ti GPUs. These are author-reported figures, not estimates for our machine.

It does not demonstrate our CPU-clock compliance. Its evaluation uses JSettlers rather than our pinned engine; the authors note rule differences, including JSettlers' resource-bank handling. The text's discard wording also differs from our strict greater-than-seven threshold. Therefore this is a close research reference, not proof of exact equivalence.

The paper links [Swynfel/rust-catan](https://github.com/Swynfel/rust-catan), a simulator. No ready-made training dataset for this paper was obtained.

## 5. Agent-approach resources collected for later reading

These are a reading catalogue, **not a chosen implementation plan**.

| Resource | Approach / subject | Player/rule evidence | Runtime and data status |
|---|---|---|---|
| [Organizer F and baseline comparisons](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md) | One-step weighted evaluation; published comparison with search bots | Exact hackathon reference | Sourced harness timings; already installed locally |
| [Gendre–Kaneko 2020](https://arxiv.org/abs/2008.07079) | Self-play actor–critic and mixed spatial/scalar encoding | Two players, 10 VP, no player trades | No proof of our clock; paper/simulator, no downloaded training corpus |
| [Gan, Li, Patel, Tay: Catan—A Probabilistic Approach](https://eric-gan.github.io/files/catan.pdf) | Expected time to victory, production rates, ports and semi-greedy planning | Explicit two-player section; course-specific Staffbot/environment | No verified pinned-engine or CPU equivalence; [PDF saved](research/downloads/papers/gan-et-al-probabilistic-approach.pdf) |
| [Guhe–Lascarides 2014](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf) | Estimated build/win time and interpretable build plans | Four-player benchmark, trading present | Paper/corpus comparison; no acquired raw corpus |
| [Driss–Cazenave: Deep Catan](https://www.lamsade.dauphine.fr/~cazenave/papers/DeepCatanEvo.pdf) | Neural value models, MCTS and Expert Iteration | Explicitly four players, imperfect information; agent refuses player trades | Different player count; no proof of our clock; [PDF saved](research/downloads/papers/driss-cazenave-deep-catan.pdf) |
| [Szita, Chaslot, Spronck: Monte-Carlo Tree Search in Settlers of Catan](https://research.tilburguniversity.edu/en/publications/monte-carlo-tree-search-in-settlers-of-catan/) | Catan-specific MCTS | Collected university publication record; related papers describe a perfect-information variant | Bibliographic lead; full source not reviewed here, not a validated implementation recommendation |
| [Long et al.: Understanding the Success of Perfect Information Monte Carlo Sampling](https://ojs.aaai.org/index.php/AAAI/article/view/7562) | Planning with sampled hidden worlds | General imperfect-information search, not this Catan benchmark | Method reference; no compatible game dataset |
| [Anthony, Tian, Barber: Thinking Fast and Slow with Deep Learning and Tree Search](https://arxiv.org/abs/1705.08439) | Expert Iteration: learning/search feedback | General method, not an exact Catan result | Method reference; no hackathon timing claim |
| [Ross, Gordon, Bagnell: DAgger](https://proceedings.mlr.press/v15/ross11a.html) | Imitation learning with iterative data aggregation | General method | Method reference; no Catan dataset |
| [Catanatron data and ML documentation](https://docs.catanatron.com/advanced/data-and-machine-learning) | State/action/reward export and representations | Docs include a two-agent `F,R` export example | **Generation capability**, not an existing corpus; no data generated now; docs may differ from pinned version |
| [PeterLP123/catanatron-1v1](https://github.com/PeterLP123/catanatron-1v1) | Search, behavioral cloning, DAgger, MaskablePPO | README preset: two players, **15 VP, balanced dice, friendly robber, discard limit 9** | Not our rules; inspected repository tree did not supply a ready dataset in standard CSV/Parquet/NPZ/JSONL/archive formats |
| [rli8145/alphahex](https://github.com/rli8145/alphahex) | Standalone 1v1 AlphaZero-style MCTS system | Separate engine; full rule compatibility not checked | Code resource, not a verified dataset or drop-in Python submission |

The Gan report is dated May 23, 2020 on its title while its header says EE126 Spring 2019; preserve that source discrepancy rather than silently resolving it. Its reported Staffbot results are not F/O results and its multiplayer sample count is not clear in the short report.

The inspected code-resource revisions were:

- `PeterLP123/catanatron-1v1`: `37b60be720e66b65f236f366be5e0ad119aacb66` (GitHub reports GPL-3.0).
- `rli8145/alphahex`: `4d5c0e22ddcdeda87250536f9de1389211731904` (GitHub reports MIT).
- `Swynfel/rust-catan`: project located; GitHub reports MIT; no installation or compilation performed.

Repository instructions and scripts were not executed. External engines were not installed into or substituted for our shared environment.

## 6. Suggested reading order only

To keep the collection usable without prematurely choosing a strategy:

1. **For the requested statistical work:** Chabot's article and the original Kaggle metadata/CSV, followed by Guhe–Lascarides' empirical strategy paper.
2. **For two-player research:** Gendre–Kaneko first, then the Gan course report. Keep their environment and timing differences visible.
3. **For later agent-method comparisons:** organizer F reference, followed by the collected sampling, imitation-learning and Expert Iteration papers.

A recommendation about which algorithm to implement, which features to use, or which strategy to try is deferred to the later analysis stage requested by the user. None of the downloaded data is currently labelled training-ready for our exact setup.

## 7. Local acquisition and verification record

All resources were fetched over public HTTPS without login, SSH or account changes. The original Kaggle ZIP and both HF Parquet files are stored under `research/downloads/datasets/`; four papers are under `research/downloads/papers/`. Downloads are excluded by the root `.gitignore` to prevent accidental inclusion in the future team repository. The source catalogue and metadata remain separate from installed environments and member workspaces.

| Saved file | Bytes | SHA-256 |
|---|---:|---|
| `lumins-catan-games.zip` | 5,453 | `c7a85f6c4f8bc01586f9ea84de7988855180e75d10399b560d7be78e2cd8a428` |
| `catanstats.csv` | 16,689 | `5d8d31fa9623391e659f275d12c8facacf202924624fd509a1c5c6abd939b6e0` |
| `g8967-catan-sft.parquet` | 7,577,830 | `360030808dd8f490bf2f104061856db7dcbfafc4b1e4f4e4b0f553a3101c1e6e` |
| `vvantim-catan-sft.parquet` | 1,485,529 | `e1c7035007de30b97c244d57223a98b2f980834d0a22b6dbf8122156b7f44c92` |

Machine-readable evidence:

- [Download manifest](research/metadata/download-manifest.json): URLs, byte sizes, content types and checksums, including papers.
- [File verification](research/metadata/FILE-VERIFICATION.json): ZIP integrity, CSV schema and Parquet marker checks.
- [Kaggle metadata](research/metadata/kaggle-lumins.json): original description, data dictionary and license.
- [HF 1v1 metadata](research/metadata/hf-g8967.json) and [preview](research/metadata/g8967-first-row.json).
- [HF second dataset metadata](research/metadata/hf-vvantim.json) and [preview](research/metadata/VVantim-first-row.json).

A read-only check found that the bundled document Python did not have `pyarrow`; no installation was attempted. The hosted viewer supplied schema and one-row previews instead. This is why complete local Parquet decoding is explicitly unverified.

No retrieved statistical claim was recomputed. No outcome-based filtering, data cleaning, quality scoring, train/test splitting or feature extraction was performed. No new simulations were generated to manufacture a matching dataset.

## 8. Stop point

**Collected:** three downloadable datasets, four local papers, primary-source links for statistical and agent research, provenance metadata, and explicit two-player/rule labels.

**Unresolved:** an exact two-player, 10-VP, no-player-trading, pinned-engine corpus compatible with our observation/action contract and timing evaluation. Its existence is not ruled out; it was not verified in this bounded collection.

**Stopped:** before independent statistical analysis, agent recommendations requiring analysis, implementation, training, four-person assignments or further environment changes.
