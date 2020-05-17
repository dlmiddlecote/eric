import json
import os
import faust

# Which Kafka should we connect to?
KAFKA_BROKER = os.getenv("KAFKA_BROKER", default="kafka://localhost:9092")

# How many partitions should we group the main topic in to?
PARTITIONS = 4

# Define a faust app. All apps with the same name will join the same consumer group.
app = faust.App("eric", broker=KAFKA_BROKER)

# Define the message that will be on the topic
class Message(faust.Record, serializer="json"):
    index: int
    name: str


# Define a kafka topic to use
topic = app.topic("msgs", value_type=Message, partitions=1, internal=True)

# Capture seen partitions in a local table.
seen = app.Table("seen", default=int, partitions=PARTITIONS).tumbling(10.0, expires=60.0, key_index=True)

## DLM: Wish that I didn't have to make the key_index changelog topic manually...
# It only gets created with 1 partition otherwise.
seen_index_topic = app.topic("eric-seen-key_index-changelog", partitions=PARTITIONS)


# How should we split the messages into partitions?
def groupby_key(msg: Message) -> str:
    return f"{msg.index % PARTITIONS}"


@app.agent(topic)
async def process(stream):
    """
    Read from the topic infinitely, printing out what we received.

    Because the stream of messages has been grouped, into n PARTITIONS, we also
    print out which partitions each processor sees, to demonstrate the automatic
    rebalancing of partitions across consumers.
    """
    async for msg in stream.group_by(groupby_key, name="groups", partitions=PARTITIONS):
        print(f"Msg(Index: {msg.index} Partition: {msg.index % PARTITIONS}): Hey, {msg.name}!")

        # Increment count of paritions that have been seen by this processor.
        seen[msg.index % PARTITIONS] += 1

        # Print out the partitions this processor has seen in the last 10s.
        print(f"Seen in last 10s: {sorted([l for l in list(seen.items()) if l[1] > 0])}")


@app.page("/metrics")
async def get_count(self, request):
    """
    Demo of web endpoint that could be used to gather metrics from each processor.
    A Prometheus exporter could be integrated here.
    """
    return self.json({"messages_received_by_topic": app.monitor.messages_received_by_topic})


@app.task
async def register_key_index():
    """
    Make sure that the seen table key index topic exists, with the correct number
    of partitions.

    This is a side effect of https://github.com/robinhood/faust/issues/473, where
    this topic isn't created before the app starts, like others.
    """
    await seen_index_topic.maybe_declare()


if __name__ == "__main__":
    app.main()
