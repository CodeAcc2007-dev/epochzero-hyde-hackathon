# B01 v001 — Bottleneck economy

Owner: Aroosh (Member 1). Primary implementation explicitly requested by the user.

Use this **agent.py** directly in the existing pinned organizer environment. Helpers are included; no sibling modules, credentials, environment directory, data or runtime provider calls.

B01 selects a viable purchase family, reserves complete ingredients, filters trades that merely replace missing cards and retains a goal during each discard. It uses actual owned port rates/current bank and refuses to re-export a resource imported earlier in the turn. Bounded deterministic same-turn search can complete enabling trades.

Frozen source/config identity is in `manifest.json`. Preserve this version; future fixes need a new version and fresh confirmation boards.

Main verification is 500 paired-seat games against unchanged F under the original clock, with 20-game process resets. See [results and limits](../../../implementation/BUILD-AND-RESULTS.md). [ZIP](../../../artifacts/B01-v001.zip) contains only the exact `agent.py`, CRC/hash verified. No SSH, portal submission or GitHub upload.
