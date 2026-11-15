
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from redis.exceptions import RedisError

from app.database.session import get_session
from app.models import URL, User
from app.schemas.urls import (
    URLCreateRequest,
    URLCreateResponse,
    URLDeleteResponse,
    URLResponse,
    URLUpdateRequest,
)
from app.services.cache import (
    get_cached_url,
    cache_url,
    invalidate_url_cache,
)
from app.services.security import get_current_user
from app.services.short_codes import short_code_generator
from app.services.rate_limiter import limiter


router = APIRouter(tags=["URLs"])


def get_url_or_404(url_id: int, user_id: int, session: Session) -> URL:
    statement = select(URL).where(
        URL.id == url_id,
        URL.user_id == user_id,
    )

    url_record = session.exec(statement).first()

    if url_record is None:
        raise HTTPException(
            status_code=404,
            detail="URL not found",
        )

    return url_record


@router.post(
    "/urls",
    response_model=URLCreateResponse,
    status_code=201,
    summary="Create a shortened URL",
)
@limiter.limit("5/minute")
def create_url(
    request: Request,
    response: Response,
    payload: URLCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid user",
        )

    for _ in range(5):
        url_record = URL(
            original_url=payload.original_url,
            short_code=short_code_generator.generate(),
            user_id=current_user.id,
        )

        session.add(url_record)

        try:
            session.commit()
            session.refresh(url_record)

            return URLCreateResponse(
                message="URL created successfully",
                original_url=url_record.original_url,
                short_code=url_record.short_code,
            )

        except IntegrityError:
            session.rollback()

    raise HTTPException(
        status_code=503,
        detail="Could not generate a unique short code. Please try again.",
    )


@router.get(
    "/urls",
    response_model=list[URLResponse],
    summary="Get all your URLs",
)
def get_all_urls(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(URL)
        .where(URL.user_id == current_user.id)
        .order_by(URL.id)
    )

    urls = session.exec(statement).all()

    return [
        URLResponse.model_validate(url)
        for url in urls
    ]


@router.get(
    "/urls/{url_id}",
    response_model=URLResponse,
    summary="Get a URL by ID",
)
def get_url(
    url_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    url_record = get_url_or_404(
        url_id,
        current_user.id,
        session,
    )

    return URLResponse.model_validate(url_record)


@router.put(
    "/urls/{url_id}",
    response_model=URLResponse,
    summary="Update a shortened URL",
)
def update_url(
    url_id: int,
    payload: URLUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    url_record = get_url_or_404(
        url_id,
        current_user.id,
        session,
    )

    url_record.original_url = payload.original_url

    session.add(url_record)
    session.commit()
    session.refresh(url_record)

    try:
        invalidate_url_cache(url_record.short_code)
    except RedisError:
        pass

    return URLResponse.model_validate(url_record)


@router.delete(
    "/urls/{url_id}",
    response_model=URLDeleteResponse,
    summary="Delete a shortened URL",
)
def delete_url(
    url_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    url_record = get_url_or_404(
        url_id,
        current_user.id,
        session,
    )

    short_code = url_record.short_code

    session.delete(url_record)
    session.commit()

    try:
        invalidate_url_cache(short_code)
    except RedisError:
        pass

    return URLDeleteResponse(
        message="URL deleted successfully",
        id=url_id,
    )


@router.get(
    "/{short_code}",
    summary="Redirect to the original URL",
)
def redirect_to_original_url(
    short_code: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:

    try:
        cached_url = get_cached_url(short_code)
    except RedisError:
        cached_url = None

    statement = (
        update(URL)
        .where(URL.short_code == short_code)
        .values(click_count=URL.click_count + 1)
        .returning(URL.original_url)
    )

    result = session.execute(statement)
    original_url = result.scalar_one_or_none()

    if original_url is None:
        session.rollback()

        raise HTTPException(
            status_code=404,
            detail="Short URL not found",
        )

    session.commit()

    if cached_url is not None:
        redirect_url = cached_url
    else:
        redirect_url = original_url

        try:
            cache_url(short_code, original_url)
        except RedisError:
            pass

    return RedirectResponse(
        url=redirect_url,
        status_code=307,
    )
