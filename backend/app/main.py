
import secrets
import string
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import URL
from app.schemas import URLCreate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()


def generate_short_code()-> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(
        secrets.choice(alphabet) for _ in range(7)
    )

@app.post("/api/urls", status_code=201)
def create_short_url(
    payload: URLCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    for _ in range(5):
        code = generate_short_code()

        url = URL(
            short_code = code,
            original_url = str(payload.original_url),
            expires_at = payload.expires_at
        )

        db.add(url)

        try:
            db.commit()
            db.refresh(url)

            return {
                "short_code": url.short_code,
                "short_url": f"{request.base_url}{url.short_code}",
                "expires_at": url.expires_at
            }

        except IntegrityError:
            db.rollback()

            # Retry only if this generate code already exists
            existing = (
                db.query(URL).filter(URL.short_code == code).first()
            )

            if existing is None: 
                raise HTTPException(
                    status_code=500,
                    detail="Cound not save URL"
                )



    raise HTTPException(
        status_code=503,
        detail="Count not generate a unique short code"
    )

@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db),
):
    url = (
        db.query(URL).filter(URL.short_code == short_code).first()
    )

    if url is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    if (
        url.expires_at is not None and 
        url.expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=410,
            detail="This short URL has expired"
        )

    return RedirectResponse(
        url=url.original_url,
        status_code=302
    )