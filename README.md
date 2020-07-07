# ~Faust~ Eric

> "There's a door."  
"Where does it go?"  
"It stays where it is, I think."

Eric is a sample application for learning how Kafka can be used in a Python and Kubernetes environment. [Faust][faust] is
the Python framework used to handle the boilerplate, as well as many of features from [Kafka Streams][streams].

For a great overview of Kafka and Kafka Streams see the [tutorial from Confluent][streams-tutorial].

[faust]: https://faust.readthedocs.io/en/latest/
[streams]: https://kafka.apache.org/documentation/streams/
[streams-tutorial]: https://www.confluent.io/blog/kafka-streams-tables-part-1-event-streaming/

## Overview

Eric implements a 'visit aggregator'. That is, an application that receives unique events that represent a visit to a
website, and counts how many visits occurred within a set window (1m intervals by default). These aggregated counts are
then streamed to a websocket, which powers a visitors dashboard.

A diagram of the architecture is included below.

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

## System Requirements

- [Docker][docker]
- [Docker Compose][docker-compose]
- [Python 3.8][python]
- [Poetry][python-poetry]
- [websocat][websocat]

[docker]: https://docs.docker.com/get-docker/
[docker-compose]: https://docs.docker.com/compose/install/
[python]: https://www.python.org/downloads/release/python-380/
[python-poetry]: https://python-poetry.org/docs/#installation
[websocat]: https://github.com/vi/websocat

## Running

```sh
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