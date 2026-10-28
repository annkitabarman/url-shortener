from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, field_validator

class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: datetime | None = None

    @field_validator("expires_at")
    @classmethod
    def validate_expiration(cls, value):
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(
                    "expires_at must include a timezone"
                )

            if value <= datetime.now(timezone.utc):
                raise ValueError("link expired")

        return value