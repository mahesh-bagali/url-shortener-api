
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy import func

from app.database.session import get_session
from app.models import URL, User
from app.services.security import get_current_user


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def get_analytics_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return total URL and click statistics for the current user."""

    statement = select(
        func.count(URL.id),
        func.coalesce(func.sum(URL.click_count), 0),
    ).where(
        URL.user_id == current_user.id
    )

    total_urls, total_clicks = session.exec(statement).one()

    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
    }


@router.get("/urls")
def get_url_analytics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Return click statistics for each URL owned by the current user."""

    statement = (
        select(URL)
        .where(URL.user_id == current_user.id)
        .order_by(URL.click_count.desc(), URL.id)
    )

    urls = session.exec(statement).all()

    return [
        {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "created_at": url.created_at,
            "click_count": url.click_count,
        }
        for url in urls
    ]


@router.get("/top-urls")
def get_top_urls(
    limit: int = 5,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Return the most-clicked URLs owned by the current user."""

    limit = max(1, min(limit, 100))

    statement = (
        select(URL)
        .where(URL.user_id == current_user.id)
        .order_by(URL.click_count.desc(), URL.id)
        .limit(limit)
    )

    urls = session.exec(statement).all()

    return [
        {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "click_count": url.click_count,
        }
        for url in urls
    ]
