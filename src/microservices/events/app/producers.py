import os

from aiokafka import AIOKafkaProducer
from aiokafka.structs import RecordMetadata

from schemas import MovieEvent, PaymentEvent, UserEvent


async def produce_event(
    topic_name: str, event: MovieEvent | UserEvent | PaymentEvent
) -> RecordMetadata:
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka:9092"),
        value_serializer=lambda v: v.encode("utf-8"),
    )
    await producer.start()
    try:
        metadata = await producer.send_and_wait(
            topic_name,
            event.model_dump_json(),
        )
        return metadata
    finally:
        await producer.stop()
