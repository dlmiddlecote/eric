import faust

app = faust.App("eric", broker="kafka://localhost:9092")

topic = app.topic("test", value_type=str)


@app.agent(topic)
async def process(stream):
    async for name in stream:
        print(f"Hey, {name}!")


@app.timer(interval=2)
async def timer():
    await process.send(value="Rincewind")


if __name__ == "__main__":
    app.main()
