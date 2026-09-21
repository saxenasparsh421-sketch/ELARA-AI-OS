"""
ELARA Live Satellite Map

Features:
- Real satellite imagery
- Live device location
- YOU marker
- MY LOCATION button
- Nearby hospitals
- Petrol pumps
- Pharmacies
- Schools
- Railway stations
- Airports
- Landmarks
- Refresh Places button
- Overpass API rate-limit protection
"""

import asyncio
import threading
import tkinter as tk
import time

import requests
import tkintermapview

from maps.location_service import LocationService


# =========================================================
# MAP TILE SERVER
# =========================================================

SATELLITE_TILE_URL = (
    "https://server.arcgisonline.com/"
    "ArcGIS/rest/services/World_Imagery/"
    "MapServer/tile/{z}/{y}/{x}"
)


# =========================================================
# OPENSTREETMAP OVERPASS SERVERS
# =========================================================

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


# =========================================================
# SETTINGS
# =========================================================

POI_RADIUS_METERS = 5000

# Minimum time between POI requests
POI_REFRESH_COOLDOWN = 60


# =========================================================
# POI LABELS
# =========================================================

POI_LABELS = {
    "hospital": "Hospital",
    "fuel": "Petrol Pump",
    "pharmacy": "Pharmacy",
    "school": "School",
    "railway": "Railway Station",
    "airport": "Airport",
    "landmark": "Landmark",
}


# =========================================================
# MAP WINDOW
# =========================================================

class MapWindow:

    def __init__(self):

        # =================================================
        # MAIN WINDOW
        # =================================================

        self.root = tk.Tk()

        self.root.title(
            "ELARA Live Satellite Map"
        )

        self.root.geometry(
            "1200x800"
        )

        self.root.configure(
            bg="black"
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )


        # =================================================
        # TITLE
        # =================================================

        self.title_label = tk.Label(
            self.root,
            text="ELARA LIVE SATELLITE MAP",
            font=("Arial", 18, "bold"),
            bg="black",
            fg="white",
        )

        self.title_label.pack(
            pady=8
        )


        # =================================================
        # BUTTON BAR
        # =================================================

        self.button_frame = tk.Frame(
            self.root,
            bg="black",
        )

        self.button_frame.pack(
            pady=5
        )


        # =================================================
        # MY LOCATION BUTTON
        # =================================================

        self.my_location_button = tk.Button(
            self.button_frame,
            text="MY LOCATION",
            font=("Arial", 11, "bold"),
            command=self.go_to_my_location,
            bg="white",
            fg="black",
            padx=18,
            pady=7,
            cursor="hand2",
        )

        self.my_location_button.pack(
            side="left",
            padx=5,
        )


        # =================================================
        # REFRESH PLACES BUTTON
        # =================================================

        self.refresh_poi_button = tk.Button(
            self.button_frame,
            text="REFRESH PLACES",
            font=("Arial", 11, "bold"),
            command=self.manual_refresh_pois,
            bg="white",
            fg="black",
            padx=18,
            pady=7,
            cursor="hand2",
        )

        self.refresh_poi_button.pack(
            side="left",
            padx=5,
        )


        # =================================================
        # MAP
        # =================================================

        self.map_widget = tkintermapview.TkinterMapView(
            self.root,
            corner_radius=0,
        )

        self.map_widget.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5,
        )


        # =================================================
        # SATELLITE MAP
        # =================================================

        self.map_widget.set_tile_server(
            SATELLITE_TILE_URL,
            max_zoom=19,
        )

        self.map_widget.set_zoom(
            16
        )


        # =================================================
        # STATUS
        # =================================================

        self.status_label = tk.Label(
            self.root,
            text="Loading satellite map...",
            font=("Arial", 11),
            bg="black",
            fg="white",
        )

        self.status_label.pack(
            pady=5
        )


        # =================================================
        # ATTRIBUTION
        # =================================================

        self.attribution_label = tk.Label(
            self.root,
            text=(
                "Satellite imagery © Esri | "
                "Places © OpenStreetMap contributors"
            ),
            font=("Arial", 8),
            bg="black",
            fg="gray",
        )

        self.attribution_label.pack(
            pady=(0, 5)
        )


        # =================================================
        # LOCATION SERVICE
        # =================================================

        self.location_service = LocationService()

        self.latest_location = None

        self.current_marker = None

        self.first_location = True

        self.running = True


        # =================================================
        # POI SYSTEM STATE
        # =================================================

        self.poi_markers = []

        self.poi_loading = False

        self.last_poi_refresh_time = 0

        self.last_poi_location = None


        # =================================================
        # START LOCATION THREAD
        # =================================================

        self.start_location_thread()


    # =====================================================
    # START LOCATION THREAD
    # =====================================================

    def start_location_thread(self):

        thread = threading.Thread(
            target=self.location_loop,
            daemon=True,
        )

        thread.start()


    # =====================================================
    # LOCATION LOOP
    # =====================================================

    def location_loop(self):

        try:

            asyncio.run(
                self.update_location()
            )

        except Exception as error:

            print(
                f"[ELARA Map] Location thread error: {error}"
            )


    # =====================================================
    # LOCATION UPDATE
    # =====================================================

    async def update_location(self):

        while self.running:

            try:

                location = (
                    await self.location_service
                    .get_device_location()
                )

                if location:

                    self.latest_location = location

                    self.root.after(
                        0,
                        self.show_location,
                        location.latitude,
                        location.longitude,
                        location.accuracy,
                    )

            except Exception as error:

                print(
                    f"[ELARA Map] Location error: {error}"
                )

            await asyncio.sleep(5)


    # =====================================================
    # SHOW LOCATION
    # =====================================================

    def show_location(
        self,
        latitude,
        longitude,
        accuracy,
    ):

        # =================================================
        # FIRST LOCATION
        # =================================================

        if self.first_location:

            self.map_widget.set_position(
                latitude,
                longitude,
            )

            self.map_widget.set_zoom(
                16
            )

            self.first_location = False

            # Load POIs once
            self.refresh_pois()


        # =================================================
        # UPDATE YOU MARKER
        # =================================================

        if self.current_marker:

            try:

                self.current_marker.set_position(
                    latitude,
                    longitude,
                )

            except Exception:

                self.current_marker = (
                    self.map_widget.set_marker(
                        latitude,
                        longitude,
                        text="YOU",
                    )
                )

        else:

            self.current_marker = (
                self.map_widget.set_marker(
                    latitude,
                    longitude,
                    text="YOU",
                )
            )


        # =================================================
        # ACCURACY
        # =================================================

        if accuracy is None:

            accuracy_text = "Unknown"

        else:

            accuracy_text = (
                f"{accuracy:.1f} m"
            )


        # =================================================
        # STATUS
        # =================================================

        self.status_label.config(
            text=(
                f"Lat: {latitude:.6f} | "
                f"Lon: {longitude:.6f} | "
                f"Accuracy: {accuracy_text}"
            )
        )


    # =====================================================
    # MY LOCATION
    # =====================================================

    def go_to_my_location(self):

        location = self.latest_location

        if location is None:

            location = (
                self.location_service
                .get_location()
            )

        if location is None:

            self.status_label.config(
                text="Live location is not available yet."
            )

            return


        latitude = location.latitude

        longitude = location.longitude


        # =================================================
        # MOVE MAP
        # =================================================

        self.map_widget.set_position(
            latitude,
            longitude,
        )


        # =================================================
        # ZOOM
        # =================================================

        self.map_widget.set_zoom(
            17
        )


        # =================================================
        # UPDATE YOU MARKER
        # =================================================

        if self.current_marker:

            try:

                self.current_marker.set_position(
                    latitude,
                    longitude,
                )

            except Exception:

                self.current_marker = (
                    self.map_widget.set_marker(
                        latitude,
                        longitude,
                        text="YOU",
                    )
                )

        else:

            self.current_marker = (
                self.map_widget.set_marker(
                    latitude,
                    longitude,
                    text="YOU",
                )
            )


        # =================================================
        # REFRESH POIs
        # =================================================

        self.manual_refresh_pois()


    # =====================================================
    # MANUAL POI REFRESH
    # =====================================================

    def manual_refresh_pois(self):

        # Manual button can bypass cooldown
        self.last_poi_refresh_time = 0

        self.refresh_pois()


    # =====================================================
    # REFRESH POIs
    # =====================================================

    def refresh_pois(self):

        location = self.latest_location

        if location is None:

            location = (
                self.location_service
                .get_location()
            )

        if location is None:

            self.status_label.config(
                text="Location required to find places."
            )

            return


        # =================================================
        # PREVENT DUPLICATE REQUEST
        # =================================================

        if self.poi_loading:

            print(
                "[ELARA POI] Request already running."
            )

            return


        # =================================================
        # COOLDOWN
        # =================================================

        current_time = time.time()

        time_since_refresh = (
            current_time -
            self.last_poi_refresh_time
        )

        if (
            time_since_refresh <
            POI_REFRESH_COOLDOWN
        ):

            remaining = int(
                POI_REFRESH_COOLDOWN -
                time_since_refresh
            )

            print(
                f"[ELARA POI] "
                f"Cooldown active: "
                f"{remaining}s"
            )

            return


        # =================================================
        # LOCATION
        # =================================================

        latitude = location.latitude

        longitude = location.longitude


        # =================================================
        # SAVE REQUEST STATE
        # =================================================

        self.poi_loading = True

        self.last_poi_refresh_time = current_time

        self.last_poi_location = (
            latitude,
            longitude,
        )


        self.status_label.config(
            text="Searching nearby places..."
        )


        # =================================================
        # BACKGROUND THREAD
        # =================================================

        thread = threading.Thread(
            target=self.load_pois,
            args=(
                latitude,
                longitude,
            ),
            daemon=True,
        )

        thread.start()


    # =====================================================
    # LOAD POIs
    # =====================================================

    def load_pois(
        self,
        latitude,
        longitude,
    ):

        query = f"""
[out:json][timeout:30];

(
    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["amenity"="hospital"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["amenity"="fuel"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["amenity"="pharmacy"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["amenity"="school"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["railway"="station"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["aeroway"="aerodrome"];

    nwr(
        around:{POI_RADIUS_METERS},
        {latitude},
        {longitude}
    )["historic"];
);

out center tags;
"""


        # =================================================
        # HEADERS
        # =================================================

        headers = {
            "User-Agent": (
                "ELARA-AI-OS/1.0 "
                "(personal desktop map application)"
            )
        }


        data = None


        # =================================================
        # TRY SERVERS
        # =================================================

        for server in OVERPASS_SERVERS:

            try:

                print(
                    f"[ELARA POI] Trying: {server}"
                )


                response = requests.post(
                    server,
                    data={
                        "data": query
                    },
                    headers=headers,
                    timeout=45,
                )


                # =================================================
                # RATE LIMIT
                # =================================================

                if response.status_code == 429:

                    print(
                        f"[ELARA POI] "
                        f"Rate limited: {server}"
                    )

                    continue


                # =================================================
                # OTHER HTTP ERRORS
                # =================================================

                response.raise_for_status()


                # =================================================
                # JSON
                # =================================================

                data = response.json()


                print(
                    f"[ELARA POI] "
                    f"Response received from {server}"
                )


                break


            except Exception as error:

                print(
                    f"[ELARA POI] "
                    f"Server failed: {error}"
                )


        # =================================================
        # ALL SERVERS FAILED
        # =================================================

        if data is None:

            self.root.after(
                0,
                self.show_poi_error,
            )

            return


        # =================================================
        # PARSE PLACES
        # =================================================

        places = []


        for element in data.get(
            "elements",
            []
        ):

            tags = element.get(
                "tags",
                {}
            )


            name = tags.get(
                "name"
            )


            if not name:

                continue


            # =================================================
            # COORDINATES
            # =================================================

            if (
                element.get("lat") is not None
                and
                element.get("lon") is not None
            ):

                poi_lat = element["lat"]

                poi_lon = element["lon"]


            elif element.get("center"):

                poi_lat = element[
                    "center"
                ]["lat"]

                poi_lon = element[
                    "center"
                ]["lon"]


            else:

                continue


            # =================================================
            # TYPE
            # =================================================

            poi_type = self.detect_poi_type(
                tags
            )


            if poi_type is None:

                continue


            places.append(
                {
                    "name": name,
                    "type": poi_type,
                    "latitude": poi_lat,
                    "longitude": poi_lon,
                }
            )


        # =================================================
        # REMOVE DUPLICATES
        # =================================================

        unique_places = {}


        for place in places:

            key = (
                place["name"],
                round(
                    place["latitude"],
                    5
                ),
                round(
                    place["longitude"],
                    5
                ),
            )


            unique_places[key] = place


        places = list(
            unique_places.values()
        )


        print(
            f"[ELARA POI] "
            f"Found {len(places)} places"
        )


        # =================================================
        # SEND TO UI
        # =================================================

        self.root.after(
            0,
            self.display_pois,
            places,
        )


    # =====================================================
    # DETECT POI TYPE
    # =====================================================

    def detect_poi_type(
        self,
        tags,
    ):

        if tags.get(
            "amenity"
        ) == "hospital":

            return "hospital"


        if tags.get(
            "amenity"
        ) == "fuel":

            return "fuel"


        if tags.get(
            "amenity"
        ) == "pharmacy":

            return "pharmacy"


        if tags.get(
            "amenity"
        ) == "school":

            return "school"


        if tags.get(
            "railway"
        ) == "station":

            return "railway"


        if tags.get(
            "aeroway"
        ) == "aerodrome":

            return "airport"


        if tags.get(
            "historic"
        ):

            return "landmark"


        return None


    # =====================================================
    # DISPLAY POIs
    # =====================================================

    def display_pois(
        self,
        places,
    ):

        # =================================================
        # REQUEST FINISHED
        # =================================================

        self.poi_loading = False


        # =================================================
        # DELETE OLD MARKERS
        # =================================================

        for marker in self.poi_markers:

            try:

                marker.delete()

            except Exception:

                pass


        self.poi_markers.clear()


        # =================================================
        # ADD NEW MARKERS
        # =================================================

        for place in places:

            poi_type = place["type"]


            label = POI_LABELS.get(
                poi_type,
                "Place",
            )


            marker_text = (
                f"{label}\n"
                f"{place['name']}"
            )


            try:

                marker = (
                    self.map_widget.set_marker(
                        place["latitude"],
                        place["longitude"],
                        text=marker_text,
                    )
                )


                self.poi_markers.append(
                    marker
                )


            except Exception as error:

                print(
                    f"[ELARA POI] "
                    f"Marker error: {error}"
                )


        # =================================================
        # STATUS
        # =================================================

        self.status_label.config(
            text=(
                f"Found {len(places)} "
                f"nearby places"
            )
        )


        print(
            f"[ELARA POI] "
            f"Displayed {len(self.poi_markers)} markers"
        )


    # =====================================================
    # POI ERROR
    # =====================================================

    def show_poi_error(self):

        self.poi_loading = False

        self.status_label.config(
            text="Nearby places could not be loaded."
        )

        print(
            "[ELARA POI] "
            "All Overpass servers failed."
        )


    # =====================================================
    # LOCATION ERROR
    # =====================================================

    def show_location_error(self):

        self.status_label.config(
            text="Unable to get device location."
        )


    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.root.mainloop()


    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        self.running = False

        self.root.destroy()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print(
        "Starting ELARA Live Satellite Map..."
    )

    app = MapWindow()

    app.run()