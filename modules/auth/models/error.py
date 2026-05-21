"""Общая модель тела HTTP-ошибки, возвращаемой FastAPI при HTTPException."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Стандартное тело ответа при HTTP-ошибке.

    FastAPI автоматически сериализует HTTPException в этот формат.

    Поля:
        detail: человекочитаемое описание причины ошибки.
    """

    detail: str
