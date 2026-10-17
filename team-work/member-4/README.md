# Anni — Member 4

The user explicitly requested primary implementation of these two assigned strategies. Initial standalone v001 candidates are built and locally verified. Research findings remain historical records; human review is still separate.

| Bot | Strategy | F main result | Direct file | Package |
| --- | --- | --- | --- | --- |
| B07 v001 | Sampled-opponent planning | 361/500, 72.2% | [agent.py](bots/B07/v001/agent.py) | [ZIP](artifacts/B07-v001.zip) |
| B08 v001 | Adaptive VP-route planning | 363/500, 72.6% | [agent.py](bots/B08/v001/agent.py) | [ZIP](artifacts/B08-v001.zip) |

Both had zero recorded errors, timeouts, crashes, clock overruns or harness random moves. Same 250 paired boards; original clock and unchanged F. The two-game difference does not establish a ranking. B07 used less CPU.

[Full evidence and limitations](implementation/BUILD-AND-RESULTS.md) · [Design decisions](implementation/DESIGN-AND-DECISIONS.md) · [Hyde contribution and review](implementation/HYDE-AND-VERIFICATION.md)

Each agent includes all helpers; use the existing organizer environment. No secrets, environment directory, runtime API key or trained weights. No SSH, portal submission or GitHub upload was performed. Default main evaluations are now 500 games per bot; extra tournaments/ablations were deferred.
