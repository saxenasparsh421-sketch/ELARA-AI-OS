"""
ELARA Location Service

Provides continuous device-location updates on Windows.

The same LocationData format can later be used by Android.
"""

import asyncio

from location.models import LocationData


class LocationService:
    def __init__(self):
        self.location = None
        self.running = False

    async def get_device_location(self):
        """Get the latest device location from Windows."""

        try:
            from winrt.windows.devices.geolocation import Geolocator

            locator = Geolocator()

            position = await locator.get_geoposition_async()

            if position is None:
                print("[LocationService] Location unavailable.")
                return None

            coordinate = position.coordinate

            self.location = LocationData(
                latitude=coordinate.point.position.latitude,
                longitude=coordinate.point.position.longitude,
                accuracy=coordinate.accuracy,
            )

            return self.location

        except Exception as e:
            print(f"[LocationService] Error: {e}")
            return None

    def get_location(self):
        """Return the most recently received location."""
        return self.location

    async def start_tracking(self, interval=5):
        """
        Continuously update device location.

        interval:
            Seconds between location requests.
        """

        self.running = True

        print("ELARA Live Location Tracking")
        print("----------------------------")
        print("Tracking started...")
        print("Press Ctrl+C to stop.\n")

        while self.running:
            location = await self.get_device_location()

            if location:
                print(
                    f"📍 "
                    f"Lat: {location.latitude:.6f} | "
                    f"Lon: {location.longitude:.6f} | "
                    f"Accuracy: {location.accuracy:.1f} m"
                )

            await asyncio.sleep(interval)

    def stop_tracking(self):
        """Stop location tracking."""
        self.running = False


async def main():
    service = LocationService()

    try:
        await service.start_tracking(interval=5)

    except KeyboardInterrupt:
        service.stop_tracking()
        print("\nELARA Live Location Tracking stopped.")


if __name__ == "__main__":
    asyncio.run(main())