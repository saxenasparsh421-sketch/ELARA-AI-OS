import json
from pathlib import Path
from datetime import datetime, timezone


CATALOG_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "map_catalog.json"
)


class MapCatalog:
    def __init__(self):
        self.catalog_file = CATALOG_FILE
        self.catalog_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.catalog_file.exists():
            self._save({
                "maps": {}
            })

    def _load(self):
        with open(self.catalog_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, data):
        with open(
            self.catalog_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(data, file, indent=2)

    def add_map(
        self,
        map_id,
        name,
        region,
        map_type="satellite",
        permanent=False,
    ):
        data = self._load()

        data["maps"][map_id] = {
            "name": name,
            "region": region,
            "type": map_type,
            "permanent": permanent,
            "downloaded": True,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._save(data)

    def remove_map(self, map_id):
        data = self._load()

        if map_id in data["maps"]:
            if data["maps"][map_id].get("permanent"):
                raise ValueError(
                    "Permanent map cannot be removed."
                )

            del data["maps"][map_id]
            self._save(data)

    def list_maps(self):
        return self._load()["maps"]


if __name__ == "__main__":
    catalog = MapCatalog()

    catalog.add_map(
        map_id="home_town",
        name="Home Town",
        region="HOME",
        map_type="satellite",
        permanent=True,
    )

    print(json.dumps(
        catalog.list_maps(),
        indent=2
    ))