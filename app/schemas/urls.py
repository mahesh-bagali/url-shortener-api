
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, TypeAdapter, field_validator

_http_url_adapter = TypeAdapter(HttpUrl)


class URLCreateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"original_url": "https://www.example.com/products"}
            ]
        }
    )

    original_url: str

    @field_validator("original_url")
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        parsed_url = _http_url_adapter.validate_python(value)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("URL must use the http or https scheme")
        return value


class URLUpdateRequest(BaseModel):
    original_url: str

    @field_validator("original_url")
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        parsed_url = _http_url_adapter.validate_python(value)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError("URL must use the http or https scheme")
        return value


class URLCreateResponse(BaseModel):
    message: str
    original_url: str
    short_code: str


class URLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int


class URLDeleteResponse(BaseModel):
    message: str
    id: int
