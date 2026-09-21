"""
ELARA Live Map

Connects live LocationData with the map layer.

The actual map renderer can be connected later
without changing the location system.
"""

from location.models import LocationData


class LiveMap:
    def __init__(self):
        self.current_location = None

    def update_location(self, location: LocationData):
        """Update the live map marker."""

        if not isinstance(location, LocationData):
            raise TypeError(
                "location must be a LocationData object"
            )

        self.current_location = location

    def get_marker(self):
        """Return data needed by the map renderer."""

        if self.current_location is None:
            return None

        return {
            "latitude": self.current_location.latitude,
            "longitude": self.current_location.longitude,
            "accuracy": self.current_location.accuracy,
            "timestamp": self.current_location.timestamp,
        }

    def clear_marker(self):
        """Remove the live location marker."""

        self.current_location = None


if __name__ == "__main__":
    live_map = LiveMap()

    test_location = LocationData(
        latitude=28.36996775,
        longitude=79.41311075,
        accuracy=292.0,
    )

    live_map.update_location(test_location)

    print("ELARA Live Map")
    print("--------------")

    marker = live_map.get_marker()

    print(f"Marker latitude : {marker['latitude']}")
    print(f"Marker longitude: {marker['longitude']}")
    print(f"Accuracy        : {marker['accuracy']} m")
    print(f"Timestamp       : {marker['timestamp']}")