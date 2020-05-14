import os
import faust

# Which Kafka should we connect to?
KAFKA_BROKER = os.getenv("KAFKA_BROKER", default="kafka://localhost:9092")

# Define a faust app
app = faust.App("eric", broker=KAFKA_BROKER)

# Define the message that will be on the topic
class Message(faust.Record, serializer='json'):
    index: int
    name: str

# Define a kafka topic to use
topic = app.topic("test", value_type=Message)


# How to partition messages
def get_group_by_key(msg: Message) -> int:
    return msg.index

# Read from the topic infinitely, and print the values
@app.agent(topic)
async def process(stream):
    async for msg in stream.group_by(get_group_by_key, name='index_partition'):
        print(f"Msg({msg.index}): Hey, {msg.name}!")


if __name__ == "__main__":
    app.main()
