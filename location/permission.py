from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class LocationConsent:
    granted: bool = False
    granted_at: str | None = None
    revoked_at: str | None = None

    def grant(self):
        self.granted = True
        self.granted_at = datetime.now(timezone.utc).isoformat()
        self.revoked_at = None

    def revoke(self):
        self.granted = False
        self.revoked_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "granted": self.granted,
            "granted_at": self.granted_at,
            "revoked_at": self.revoked_at,
        }