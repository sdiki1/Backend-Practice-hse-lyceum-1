import datetime

from pydantic import BaseModel, ConfigDict


class PostModelDTO(BaseModel):
    """
    DTO for post models.

    It returned when accessing post models from the API.
    """

    id: int
    title: str
    content: str
    updated_at: datetime.datetime
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class PostModelInputDTO(BaseModel):
    """DTO for creating new post model."""

    title: str
    content: str


class PostModelUpdateDTO(BaseModel):
    """DTO for edit post model."""

    title: str = ""
    content: str = ""
