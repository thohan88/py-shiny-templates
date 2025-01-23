from shiny import ui, App, reactive
from shinywidgets import render_widget, output_widget
from ipyleaflet import Marker, Map, Icon, basemaps
from pathlib import Path
import json
import math
import time

app_dir = Path(__file__).parent


def calc_pos(lat, lon, heading, speed, elapsed_time, playback_speed):
    speed_mps = speed * playback_speed * 0.514444  # 1 knot = 0.514444 m/s
    distance = speed_mps * elapsed_time
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    heading_rad = math.radians(heading)
    R = 6371000  # Mean radius of the Earth

    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance / R)
        + math.cos(lat_rad) * math.sin(distance / R) * math.cos(heading_rad)
    )

    new_lon_rad = lon_rad + math.atan2(
        math.sin(heading_rad) * math.sin(distance / R) * math.cos(lat_rad),
        math.cos(distance / R) - math.sin(lat_rad) * math.sin(new_lat_rad),
    )

    return math.degrees(new_lat_rad), math.degrees(new_lon_rad)


with open(app_dir / "flights.json", "r") as f:
    flight_data = json.load(f)

app_ui = ui.page_fillable(
    ui.head_content(
        ui.tags.title("Leaflet live positions"),
        ui.tags.style(
            """ 
            .bslib-page-fill {padding: 0 !important;}
            .jupyter-widgets {margin: 0 !important;}
            .map-inputs {z-index:1000 !important;}
            """
        )
    ),
    ui.panel_absolute(
        ui.card(
            ui.card_body(
                ui.input_slider(
                    "playback_speed",
                    ui.tags.span("Playback speed", class_="small text-muted"),
                    value=1,
                    min=1,
                    max=5,
                    post="x",
                ),
                ui.input_slider(
                    "refresh_interval",
                    ui.tags.span("Refresh interval", class_="small text-muted"),
                    value=0.5,
                    min=0.05,
                    max=3,
                    step=0.05,
                    post="s",
                ),
                ui.layout_columns(
                    ui.input_action_button(
                        "reset", "Reset", class_="btn btn-sm btn-light"
                    ),
                    ui.input_action_button(
                        "quick", "Quick!", class_="btn btn-sm btn-light"
                    ),
                    gap=5,
                    class_="p-0 m-0",
                ),
            ),
            class_="mb-0",
        ),
        width="200px",
        left="10px",
        bottom="10px",
        draggable=False,
        class_="map-inputs",
    ),
    output_widget("map"),
    fillable_mobile=True
)


def server(input, output, session):

    ICON = Icon(icon_url="plane.svg", icon_size=(40, 40), icon_anchor=(20, 20))
    m = Map(center=(59.95, 10.76), zoom=9, basemap=basemaps.CartoDB.Positron)
    markers = {}

    @render_widget
    def map():
        return m

    start_time = reactive.value(time.time())

    @reactive.calc
    def elapsed_time():
        reactive.invalidate_later(input.refresh_interval())
        return time.time() - start_time()

    @reactive.effect
    @reactive.event(input.quick)
    def quick_playback():
        ui.update_slider("playback_speed", value=5)
        ui.update_slider("refresh_interval", value=0.1)

    @reactive.effect
    @reactive.event(input.reset)
    def reset_playback():
        ui.update_slider("playback_speed", value=1)
        ui.update_slider("refresh_interval", value=0.5)
        start_time.set(time.time())

    @reactive.effect
    def update_markers():
        for flight in flight_data:

            callsign = flight["callsign"]

            lat, lon = calc_pos(
                flight["latitude"],
                flight["longitude"],
                flight["heading"],
                flight["speed"],
                elapsed_time(),
                input.playback_speed(),
            )

            if callsign in markers:
                markers[callsign].location = (lat, lon)
            else:
                markers[callsign] = Marker(
                    icon=ICON,
                    location=(lat, lon),
                    rotation_angle=flight["heading"],
                    rotation_origin="20px 20px",
                )
                m.add(markers[callsign])


app = App(app_ui, server, static_assets=app_dir / "www")
