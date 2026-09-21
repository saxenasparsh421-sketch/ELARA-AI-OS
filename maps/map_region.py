"""
ELARA Map Region

Defines geographic regions used by the offline map system.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MapRegion:
    """
    Geographic bounding box.

    north:
        Northern latitude

    south:
        Southern latitude

    east:
        Eastern longitude

    west:
        Western longitude
    """

    region_id: str
    name: str

    north: float
    south: float
    east: float
    west: float

    map_type: str = "satellite"

    def center(self):
        """Return the center latitude and longitude."""

        latitude = (self.north + self.south) / 2
        longitude = (self.east + self.west) / 2

        return latitude, longitude

    def to_dict(self):
        """Convert the region to a dictionary."""

        return {
            "region_id": self.region_id,
            "name": self.name,
            "north": self.north,
            "south": self.south,
            "east": self.east,
            "west": self.west,
            "type": self.map_type,
        }


# Permanent hometown region.
#
# These are initial approximate boundaries for the
# Bareilly urban area. They can be refined later.
BAREILLY_REGION = MapRegion(
    region_id="bareilly",
    name="Bareilly, Uttar Pradesh, India",

    north=28.45,
    south=28.30,

    east=79.50,
    west=79.35,

    map_type="satellite",
)


if __name__ == "__main__":

    region = BAREILLY_REGION

    print("ELARA Map Region")
    print("----------------")

    print(f"ID      : {region.region_id}")
    print(f"Name    : {region.name}")
    print(f"Type    : {region.map_type}")

    print("\nBounding Box:")
    print(f"North   : {region.north}")
    print(f"South   : {region.south}")
    print(f"East    : {region.east}")
    print(f"West    : {region.west}")

    latitude, longitude = region.center()

    print("\nCenter:")
    print(f"Latitude : {latitude}")
    print(f"Longitude: {longitude}")