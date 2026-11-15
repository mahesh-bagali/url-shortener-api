
import pytest
from pydantic import ValidationError

from app.schemas.urls import URLCreateRequest, URLUpdateRequest


class TestURLCreateValidation:

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.example.com",
            "http://example.com",
            "https://example.com/products?id=10",
        ],
    )
    def test_valid_urls_are_accepted(self, url):
        payload = URLCreateRequest(original_url=url)

        assert payload.original_url == url

    @pytest.mark.parametrize(
        "url",
        [
            "not-a-url",
            "example.com",
            "ftp://example.com",
            "https://",
        ],
    )
    def test_invalid_urls_are_rejected(self, url):
        with pytest.raises(ValidationError):
            URLCreateRequest(original_url=url)


class TestURLUpdateValidation:

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.example.com",
            "http://example.com",
        ],
    )
    def test_valid_urls_are_accepted(self, url):
        payload = URLUpdateRequest(original_url=url)

        assert payload.original_url == url

    @pytest.mark.parametrize(
        "url",
        [
            "not-a-url",
            "example.com",
            "ftp://example.com",
            "https://",
        ],
    )
    def test_invalid_urls_are_rejected(self, url):
        with pytest.raises(ValidationError):
            URLUpdateRequest(original_url=url)
