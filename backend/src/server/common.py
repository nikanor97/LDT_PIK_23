import enum
from typing import Any, Generic, Optional, Protocol, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel, validator
from pydantic.generics import GenericModel


class METHOD:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class RouterProtocol(Protocol):
    router: APIRouter


Model_T = TypeVar("Model_T", bound=BaseModel | list)


class UnifiedResponse(GenericModel, Generic[Model_T]):
    # data: Optional[Model_T | list[Model_T]] = None
    data: Optional[Model_T] = None
    error: Optional[str] = None  # list here cause error is always exception.args
    error_metadata: Optional[Any] = None
    status_code: int = 200

    @validator("data")
    def data_is_empty_list(cls, v):
        """
        Without this validator if data is an empty list, UnifiedResponse validation will fail
        Somehow if data is an empty list, it is considered by pydantic as BaseModel()
        """
        return [] if v == BaseModel() else v


class HTTPExceptionDetailErrorMetaOptions(str, enum.Enum):
    field = "field"


class HTTPExceptionDetail(BaseModel):
    """
    List of these HTTPExceptionDetail objects can be used in HTTPException details section
    """

    error: str
    error_meta: dict[HTTPExceptionDetailErrorMetaOptions, str]

    # class Config:
    #     json_encoders = {
    #         'HTTPExceptionDetail': lambda x: jsonable_encoder(x)
    #     }


def exc_to_str(exception: Exception) -> str:
    return "\n".join([arg for arg in exception.args])
