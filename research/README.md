# Research resources: source links and local files

The [main catalogue](../03-RESEARCH-AND-DATASET-CATALOGUE.md) is the authoritative list of collected sources, revisions, licenses, numerical claims and limitations. The [root README](../README.md) gives direct dataset-page links for a quick start.

## Included in the team repository (currently public)

- Publisher metadata for Kaggle and both Hugging Face datasets.
- [Acquisition manifest](metadata/download-manifest.json): public source URLs, revisions where applicable, byte counts and SHA-256 hashes.
- [File-verification record](metadata/FILE-VERIFICATION.json): ZIP/CSV and Parquet-marker checks, including their limits.
- Saved 43k collection README/release availability evidence. This is documentation; its raw corpus was not acquired.

These provenance files do not make the external corpora exact-match, expert-labelled or training-ready.

## Intentionally local and excluded from Git

| Local destination | Obtain from |
|---|---|
| `downloads/datasets/lumins-catan-games.zip` and extracted `catanstats.csv` | [Kaggle source](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games); [original ZIP API](https://www.kaggle.com/api/v1/datasets/download/lumins/settlers-of-catan-games) |
| `downloads/datasets/g8967-catan-sft.parquet` | [Pinned HF file](https://huggingface.co/datasets/g8967/catan-sft-dataset/resolve/0a4a50a84354338300d4ef10d6177378bb34a2f9/data/train-00000-of-00001.parquet) |
| `downloads/datasets/vvantim-catan-sft.parquet` | [Pinned HF file](https://huggingface.co/datasets/VVantim/catan-sft-data/resolve/aa0667e6bc37f05f0c4e85bed6ccb3b5f77e9957/data/train-00000-of-00001.parquet) |
| `downloads/papers/gendre-kaneko-2020-cross-dimensional.pdf` | [Two-player RL paper](https://arxiv.org/abs/2008.07079) |
| `downloads/papers/guhe-lascarides-2014-strategies.pdf` | [University-hosted paper](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf) |
| `downloads/papers/gan-et-al-probabilistic-approach.pdf` | [Author-hosted report](https://eric-gan.github.io/files/catan.pdf) |
| `downloads/papers/driss-cazenave-deep-catan.pdf` | [Author-hosted paper](https://www.lamsade.dauphine.fr/~cazenave/papers/DeepCatanEvo.pdf) |
| `metadata/g8967-first-row.json`, `metadata/VVantim-first-row.json` | Local hosted-viewer snapshots containing sample rows; omitted from Git. Use the dataset pages' viewer when needed. |

Restore only resources needed for your assigned research, respecting source terms. Compare their hashes with the manifest/catalogue. Do not interpret a GitHub clone as transferring these local files or the shared environment. Keep raw inputs unchanged and place derived research outputs under your member folder.

The manifest also describes excluded downloads and a file-verification record may mention local previews. Those references preserve provenance; they do not imply the bytes are committed. Full Parquet decoding/whole-corpus consistency was not established during collection.

## Subsequent research audits

The original collection statements above are historical. [Aroosh's CSV audit](../team-work/member-1/phase-1/01-DATA-AND-STATISTICS.md) reproduces selected statistics and records parsing/confounding limits. [Anni's corpus audit](../team-work/member-4/phase-1/01-DATASET-AUDIT.md) now fully decodes both Parquet tables and checks specified patterns. Neither corpus is accepted for direct exact-rules training. All raw downloads/previews and the isolated reader remain excluded from Git.
