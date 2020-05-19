# ~Faust~ Eric

> "There's a door."  
"Where does it go?"  
"It stays where it is, I think."

## Overview

### Diagram
```
                                                                                ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                                               ┏━━━━━━━━━━━━━━━━━━━━┓              Consumer Group:         │
                                               ┃                    ┃           │    visit-aggregator
                                               ┃  Topic:            ┃              ╔═════════════════════╗ │
                                      ┌───────▶┃    repartition-1   ┃──────┐    │  ║  Agent:             ║
                                      │        ┃                    ┃      │       ║    process-visits   ║ │
                                      │        ┃                    ┃      │    │  ║                     ║
                                      │        ┗━━━━━━━━━━━━━━━━━━━━┛      ├──────▶║ ┌────────────────┐  ║─┼─────┐
                                      │        ┏━━━━━━━━━━━━━━━━━━━━┓      │    │  ║ │  Table         │  ║       │
                                      │        ┃                    ┃      │       ║ └────────────────┘  ║ │     │
                                      │        ┃  Topic:            ┃      │    │  ╚═════════════════════╝       │        ┏━━━━━━━━━━━━━━━━━━━━┓        ╔════════════════════╗
                                      ├───────▶┃    repartition-2   ┃──────┘                 *             │     │        ┃                    ┃        ║                    ║
         ┏━━━━━━━━━━━━━━━━━━━━┓       │        ┃                    ┃           │            *                   │        ┃  Topic:            ┃        ║  Agent:            ║
         ┃                    ┃       │        ┃                    ┃                        *             │     ├┬──────▶┃   active-visitors  ┃───────▶║   process-active-  ║
         ┃    Topic:          ┃       │        ┗━━━━━━━━━━━━━━━━━━━━┛           │            *                   │ ┐      ┃                    ┃        ║     visitors       ║
         ┃      visits        ┃──────┬▶        ┏━━━━━━━━━━━━━━━━━━━━┓              ╔═════════════════════╗ │     │        ┃                    ┃        ║                    ║
         ┃                    ┃     ┌ │        ┃                    ┃           │  ║  Agent:             ║       │ └      ┗━━━━━━━━━━━━━━━━━━━━┛        ╚════════════════════╝
         ┃                    ┃    ┌  │        ┃  Topic:            ┃              ║    process-visits   ║ │     │  └
         ┗━━━━━━━━━━━━━━━━━━━━┛   ┌   ├───────▶┃    repartition-3   ┃──────┐    │  ║                     ║       │   └
                                 ┌    │        ┃                    ┃      ├──────▶║ ┌────────────────┐  ║─┼─────┘    └
                                ┌     │        ┃                    ┃      │    │  ║ │  Table         │  ║             └
                               ┌      │        ┗━━━━━━━━━━━━━━━━━━━━┛      │       ║ └────────────────┘  ║ │            └
                              ┌       │        ┏━━━━━━━━━━━━━━━━━━━━┓      │    │  ╚═════════════════════╝               └
                             ┌        │        ┃                    ┃      │                               │              └
                            ┌         │        ┃  Topic:            ┃      │    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─                └
                           ┌          └───────▶┃    repartition-4   ┃──────┘                                                └
                          ┌                    ┃                    ┃                                                        └
                         ┌                     ┃                    ┃                                                         └
                                               ┗━━━━━━━━━━━━━━━━━━━━┛                                               ┌──────────┴─────────────┐
            ┌────────────┴────────────┐                                                                             │                        │
            │                         │                                                                             │ Only 1 active-visitors │
            │     Group visits by     │                                                                             │partition to collate all│
            │ (account_id, store_id)  │                                                                             │        counts.         │
            │hash, so that they always│                                                                             │                        │
            │go to the same agent for │                                                                             └────────────────────────┘
            │        counting.        │
            │                         │
            └─────────────────────────┘
```

## Requirements

- Docker
- Docker Compose
- Python 3.8
- Poetry
- websocat

## Running

```
# start kafka and install dependencies
make up

# run consumer
make run

# connect to websocket
websocat ws://127.0.0.1:6066/ws

# run producer
make producer

# run a more interesting producer
poetry run python -m visit_aggregator produce --account-id 1 --account-id 2 --account-id 3 --store-id us --store-id uk --frequency 2

# run another consumer
poetry run python -m visit_aggregator worker -l info --web-port 6067
```

## Kubernetes

TODO.