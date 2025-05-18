import logging
import os

from aiokafka import AIOKafkaConsumer

log = logging.getLogger("uvicorn.error")


async def consume_topics() -> None:
    consumer = AIOKafkaConsumer(
        "movie-events",
        "user-events",
        "payment-events",
        bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka:9092"),
        group_id="events-consumer-group",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            log.info(
                f"Received message from topic {msg.topic}: "
                f"{msg.value.decode()}"
            )
    finally:
        await consumer.stop()
