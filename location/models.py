from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class LocationData:
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            accuracy=(
                float(data["accuracy"])
                if data.get("accuracy") is not None
                else None
            ),
            timestamp=data.get("timestamp"),
        )