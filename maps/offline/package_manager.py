"""
ELARA Offline Map Package Manager

Manages downloaded offline map regions.

The actual satellite imagery provider can be connected later.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

from maps.map_region import MapRegion


MAP_ROOT = Path(__file__).resolve().parent.parent

PACKAGE_DIR = MAP_ROOT / "data" / "packages"
INDEX_FILE = MAP_ROOT / "data" / "offline_packages.json"


class OfflineMapPackageManager:

    def __init__(self):
        PACKAGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        if not INDEX_FILE.exists():
            self._save({
                "packages": {}
            })

    def _load(self):
        with open(
            INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def _save(self, data):
        with open(
            INDEX_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=2
            )

    def register_package(
        self,
        package_id,
        name,
        region: MapRegion,
        permanent=False,
        size_mb=0,
    ):
        """
        Register an offline map package.
        """

        if not isinstance(region, MapRegion):
            raise TypeError(
                "region must be a MapRegion object"
            )

        data = self._load()

        data["packages"][package_id] = {
            "name": name,
            "region": region.to_dict(),
            "type": region.map_type,
            "permanent": permanent,
            "downloaded": True,
            "size_mb": size_mb,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._save(data)

    def list_packages(self):
        """
        Return all registered offline map packages.
        """

        return self._load()["packages"]

    def remove_package(self, package_id):
        """
        Remove a non-permanent map package.
        """

        data = self._load()

        package = data["packages"].get(package_id)

        if package is None:
            return False

        if package.get("permanent"):
            raise ValueError(
                "Permanent map package cannot be removed."
            )

        package_path = PACKAGE_DIR / package_id

        if package_path.exists():
            shutil.rmtree(package_path)

        del data["packages"][package_id]

        self._save(data)

        return True


if __name__ == "__main__":

    manager = OfflineMapPackageManager()

    # Permanent hometown map
    home_region = MapRegion(
        region_id="bareilly",
        name="Bareilly, Uttar Pradesh, India",
        north=28.45,
        south=28.30,
        east=79.50,
        west=79.35,
        map_type="satellite",
    )

    manager.register_package(
        package_id="home_town_satellite",
        name="Home Town Satellite",
        region=home_region,
        permanent=True,
        size_mb=0,
    )

    print("ELARA Offline Map Packages")
    print("--------------------------")

    print(
        json.dumps(
            manager.list_packages(),
            indent=2
        )
    )