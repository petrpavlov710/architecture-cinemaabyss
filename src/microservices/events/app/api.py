import asyncio
import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from consumers import consume_topics
from producers import produce_event
from schemas import (
    ErrorModel,
    Event,
    EventResponse,
    MovieEvent,
    PaymentEvent,
    UserEvent,
)

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up Kafka consumer")
    asyncio.create_task(consume_topics())
    log.info("Kafka consumer started")
    try:
        yield
    finally:
        log.info("Shutting down Kafka consumer")
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    log.error(f"Exception occurred: {exc}")
    return ErrorModel(error=str(exc))


@app.get("/api/events/health")
async def healthcheck():
    return {"status": True}


@app.post(
    "/api/events/movie",
    response_model=EventResponse[MovieEvent],
    status_code=201,
)
async def add_event_movie(event: MovieEvent) -> EventResponse[MovieEvent]:
    metadata = await produce_event("movie-events", event)
    log.info(f"Produced movie event: {event}")

    return EventResponse(
        status="success",
        partition=metadata.partition,
        offset=metadata.offset,
        event=Event(
            id=f"movie-{event.movie_id}-viewed",
            type="movie",
            timestamp=datetime.datetime.now(),
            payload=event,
        ),
    )


@app.post(
    "/api/events/user",
    response_model=EventResponse[UserEvent],
    status_code=201,
)
async def add_event_user(event: UserEvent) -> EventResponse[UserEvent]:
    metadata = await produce_event("user-events", event)
    log.info(f"Produced user event: {event}")

    return EventResponse(
        status="success",
        partition=metadata.partition,
        offset=metadata.offset,
        event=Event(
            id=f"user-{event.user_id}-created",
            type="user",
            timestamp=datetime.datetime.now(),
            payload=event,
        ),
    )


@app.post(
    "/api/events/payment",
    response_model=EventResponse[PaymentEvent],
    status_code=201,
)
async def add_event_payment(event: PaymentEvent) -> EventResponse[PaymentEvent]:
    metadata = await produce_event("payment-events", event)
    log.info(f"Produced payment event: {event}")

    return EventResponse(
        status="success",
        partition=metadata.partition,
        offset=metadata.offset,
        event=Event(
            id=f"payment-{event.payment_id}-completed",
            type="payment_id",
            timestamp=datetime.datetime.now(),
            payload=event,
        ),
    )
