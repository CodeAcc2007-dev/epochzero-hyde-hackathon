# B02 v001 — City/dev engine

Owner: Aroosh (Member 1). Primary implementation explicitly requested by the user.

Use this **agent.py** directly in the existing pinned organizer environment. Helpers are included; no sibling modules, credentials, environment directory, data or runtime provider calls.

B02 adds state-dependent city commitments and wheat/ore/sheep opening investment, with probability-weighted dev/Army value and a cap on unused development cards. Investment yields to known wins, and legal expansion remains available when city supply/pieces are blocked. No draw or Army award is assumed certain.

Frozen source/config identity is in `manifest.json`. Preserve this version; future fixes need a new version and fresh confirmation boards.

Main verification is 500 paired-seat games against unchanged F under the original clock, with 20-game process resets. See [results and limits](../../../implementation/BUILD-AND-RESULTS.md). [ZIP](../../../artifacts/B02-v001.zip) contains only the exact `agent.py`, CRC/hash verified. No SSH, portal submission or GitHub upload.
