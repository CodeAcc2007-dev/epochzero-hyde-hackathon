# Prior Evidence Table (supplied records, as-is)

Common F SHA-256 (all eight records): `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613`

| Bot/Version | Wins/Games | Percentage | Seed0..Seed0+249 | Mean CPU ms | Evidence Kind | OS |
|---|---|---|---|---|---|---|
| B01/v002 | 371/500 | 74.2% | 935000..935249 | 215.3 | existing local frozen result | Linux local |
| B02/v002 | 357/500 | 71.4% | 935000..935249 | 193.62 | existing local frozen result | Linux local |
| B03/v003 | 260/500 | 52.0% | 933000..933249 | 173.38 | uploaded evidence, audited but not replayed locally | WSL |
| B04/v003 | 216/500 | 43.2% | 933500..933749 | 183.86 | uploaded evidence, audited but not replayed locally | WSL |
| B05/v004 | 375/500 | 75.0% | 934000..934249 | 167.68 | existing local frozen result | Linux local |
| B06/v004 | 356/500 | 71.2% | 934000..934249 | 104.2 | existing local frozen result | Linux local |
| B07/v002 | 369/500 | 73.8% | 934000..934249 | 125.02 | existing local frozen result | Linux local |
| B08/v002 | 359/500 | 71.8% | 934000..934249 | 363.36 | existing local frozen result | Linux local |

These records come from different board groups (four distinct seed0 blocks) and two different machines (Linux local vs WSL); this prohibits treating the table as an eight-bot matched ranking.

The B03 and B04 uploaded records were audited locally from immutable Git objects, but the games were not replayed here.
