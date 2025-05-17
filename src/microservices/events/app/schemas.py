from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ErrorModel(BaseModel):
    error: str


class Event(BaseModel, Generic[T]):
    id: str
    type: str
    timestamp: datetime
    payload: T


class EventResponse(BaseModel, Generic[T]):
    status: str
    partition: int
    offset: int
    event: Event[T]


class MovieEvent(BaseModel):
    movie_id: int
    title: str
    action: str
    user_id: int | None = None
    rating: float | None = None
    genres: list[str] | None = None
    description: str | None = None


class UserEvent(BaseModel):
    user_id: int
    username: str | None = None
    email: str | None = None
    action: str
    timestamp: datetime


class PaymentEvent(BaseModel):
    payment_id: int
    user_id: int
    amount: float
    status: str
    timestamp: datetime
    method_type: str | None = None
