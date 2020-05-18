# ~Faust~ Eric

> "There's a door."  
"Where does it go?"  
"It stays where it is, I think." 

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
poetry run python -m visit_aggregator produce --account-id 1 --account-id 2 --account-id 3 --store-id us --store-id nz --frequency 2 --max-messages 1

# run another consumer
poetry run python -m visit_aggregator worker -l info --web-port 6067
```

## Kubernetes

TODO.