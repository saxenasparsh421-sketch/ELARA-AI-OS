import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class LocationShare:
    token: str
    expires_at: str
    active: bool = True

    @classmethod
    def create(cls, duration_minutes=60):
        token = secrets.token_urlsafe(32)

        expires = datetime.now(timezone.utc) + timedelta(
            minutes=duration_minutes
        )

        return cls(
            token=token,
            expires_at=expires.isoformat(),
            active=True,
        )

    def revoke(self):
        self.active = False

    def to_dict(self):
        return {
            "token": self.token,
            "expires_at": self.expires_at,
            "active": self.active,
        }