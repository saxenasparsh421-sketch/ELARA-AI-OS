from pathlib import Path


# Root directory for ELARA map data
MAP_ROOT = Path(__file__).resolve().parent

# Local map data
MAP_DATA_DIR = MAP_ROOT / "data"

# Map styles
MAP_STYLES_DIR = MAP_ROOT / "styles"

# Temporary/cache files
MAP_CACHE_DIR = MAP_ROOT / "cache"

# Main offline map file.
# We will add the actual map dataset later.
OFFLINE_MAP_FILE = MAP_DATA_DIR / "elara_map.pmtiles"


def ensure_map_directories():
    """Create required map directories if they don't exist."""
    MAP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    MAP_STYLES_DIR.mkdir(parents=True, exist_ok=True)
    MAP_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_map_file():
    """Return the path of the configured offline map."""
    return OFFLINE_MAP_FILE


if __name__ == "__main__":
    ensure_map_directories()

    print("ELARA Map Configuration")
    print("-----------------------")
    print(f"Map data   : {MAP_DATA_DIR}")
    print(f"Map styles : {MAP_STYLES_DIR}")
    print(f"Map cache  : {MAP_CACHE_DIR}")
    print(f"Map file   : {OFFLINE_MAP_FILE}")