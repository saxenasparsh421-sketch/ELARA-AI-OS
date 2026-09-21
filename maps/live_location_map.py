"""
ELARA Live Location Map

Connects the real Windows device location
to the LiveMap marker.
"""

import asyncio

from maps.location_service import LocationService
from maps.live_map import LiveMap


async def main():
    location_service = LocationService()
    live_map = LiveMap()

    print("ELARA Live Location Map")
    print("-----------------------")
    print("Starting live map connection...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            location = await location_service.get_device_location()

            if location:
                live_map.update_location(location)

                marker = live_map.get_marker()

                print(
                    f"📍 "
                    f"Lat: {marker['latitude']:.6f} | "
                    f"Lon: {marker['longitude']:.6f} | "
                    f"Accuracy: {marker['accuracy']:.1f} m"
                )

            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\nELARA Live Location Map stopped.")


if __name__ == "__main__":
    asyncio.run(main())