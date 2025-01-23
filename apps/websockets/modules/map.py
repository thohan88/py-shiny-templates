from shiny import module, reactive, ui, req, App
from shinywidgets import output_widget, render_widget
from ipyleaflet import Map, basemaps
from ipywidgets import HTML
from pathlib import Path
from .live import mod_live_server
from .codespace import mod_codespace_server, mod_codespace_ui, PROVIDERS
from ipyleaflet import (
    DivIcon,
    LayerGroup,
    Map,
    Marker,
    ZoomControl,
)
import json


@module.ui
def mod_map_ui():
    app_ui = output_widget("map")
    return app_ui


@module.server
def mod_map_server(input, output, session, codespace_id, data):
    m = Map(
        basemap=basemaps.CartoDB.Positron,
        center=[60.39, 5.32],
        zoom=8,
        zoom_control=False,
    )
    marker_layer = LayerGroup(name="Vehicle Markers")
    m.add(marker_layer)
    m.add(ZoomControl(position="topright"))
    markers = reactive.Value({})

    @render_widget
    def map():
        return m


    @reactive.effect
    @reactive.event(codespace_id)
    def update_map_center():
        center = PROVIDERS["centers"].get(codespace_id())
        if center:
            m.center = [center["longitude"], center["latitude"]]
            m.zoom = center["zoom"]

    @reactive.effect
    def update_markers():
        req(data() is not None and not data().empty)
        vehicles = json.loads(data()["vehicles"][0])
        current_markers = markers.get()
        for vehicle in vehicles:
            location = (vehicle["latitude"], vehicle["longitude"])
            vehicle_id = vehicle["vehicle_id"]
            if vehicle_id in current_markers:
                current_markers[vehicle_id].location = location
            else:
                html_label = ui.div(
                    ui.div(
                        vehicle["line_code"] or vehicle["line_ref"] or "",
                        class_="map-marker",
                    ),
                    ui.span(vehicle["destination"] or "", class_="map-label"),
                    class_="map-marker-container",
                ).get_html_string()
                label = DivIcon(location=location, html=html_label, icon_size=(25, 25))
                marker = Marker(
                    location=location,
                    icon=label,
                    popup=HTML(vehicle["line_name"]),
                    draggable=False,
                )
                current_markers[vehicle_id] = marker
                marker_layer.add(marker)



def mod_map_app():

    app_ui = ui.page_navbar(
        ui.head_content(ui.include_css(Path(__file__).parent.parent / "styles.css")),
        ui.nav_panel("Map", mod_map_ui("map")),
        sidebar=ui.sidebar(
            mod_codespace_ui("codespace"),
            ui.input_switch("get_live_data", "Get live data", True),
        ),
        fillable=True,
    )

    def server(input, output, session):
        codespace_id = mod_codespace_server("codespace")
        data = mod_live_server("live", input.get_live_data, codespace_id)
        mod_map_server("map", codespace_id, data)

    return App(app_ui, server)
