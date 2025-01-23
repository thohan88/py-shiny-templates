from shiny import module, reactive, render, ui, App
from ipyleaflet import Map
from shinywidgets import render_widget, output_widget

PROVIDERS = {
    "selectize": {
        "All providers": {"ALL": "All Traffic"},
        "Single providers": {
            "AKT": "Agder (AKT)",
            "ATB": "Trøndelag (AtB)",
            "SKY": "Vestland (Skyss)",
            "BRA": "Viken (Brakar)",
            "GJB": "Vy (formerly NSB) Gjøvikbanen",
            "INN": "Innlandet (Innlandstrafikk)",
            "KOL": "Rogaland (Kolumbus)",
            "MOR": "Møre og Romsdal (Fram)",
            "NBU": "Connect Bus Flybuss",
            "NOR": "Nordland fylkeskommune",
            "FIN": "Troms og Finnmark (Snelandia)",
            "TRO": "Troms og Finnmark (Troms fylkestrafikk)",
            "NSB": "Vy",
            "OST": "Viken (Østfold kollektivtrafikk)",
            "SOF": "Vestland (Kringom)",
            "VKT": "Vestfold og Telemark (VKT)",
            "VOT": "Vestfold og Telemark",
        },
    },
    "centers": {
        "ALL": {"longitude": 64.836, "latitude": 16.848, "zoom": 5},
        "AKT": {"longitude": 58.168, "latitude": 7.995, "zoom": 11},
        "ATB": {"longitude": 63.422, "latitude": 10.400, "zoom": 12},
        "BRA": {"longitude": 59.757, "latitude": 10.043, "zoom": 8},
        "FIN": {"longitude": 70.065, "latitude": 23.680, "zoom": 6},
        "GJB": {"longitude": 60.119, "latitude": 10.809, "zoom": 9},
        "INN": {"longitude": 60.805, "latitude": 10.822, "zoom": 9},
        "KOL": {"longitude": 58.956, "latitude": 5.716, "zoom": 9},
        "MOR": {"longitude": 62.572, "latitude": 6.771, "zoom": 9},
        "NBU": {"longitude": 59.951, "latitude": 10.857, "zoom": 12},
        "NOR": {"longitude": 67.292, "latitude": 14.445, "zoom": 11},
        "NSB": {"longitude": 59.908, "latitude": 10.805, "zoom": 9},
        "OST": {"longitude": 59.425, "latitude": 11.173, "zoom": 9},
        "SKY": {"longitude": 60.385, "latitude": 5.324, "zoom": 11},
        "SOF": {"longitude": 61.847, "latitude": 6.081, "zoom": 10},
        "TRO": {"longitude": 69.656, "latitude": 18.957, "zoom": 12},
        "VKT": {"longitude": 59.411, "latitude": 10.543, "zoom": 12},
        "VOT": {"longitude": 59.229, "latitude": 10.209, "zoom": 9},
    },
}


@module.ui
def mod_codespace_ui():

    # Prefer Bergen at night (more traffic) and Trondheim during day (higher update frequency) 
    from datetime import datetime, time, timezone
    is_night = (lambda now: time(23, 0) <= now.time() or now.time() < time(5, 0))(datetime.now(timezone.utc))
    selected = "SKY" if is_night else "ATB"

    app_ui = ui.input_selectize(
        "codespace",
        "Choose a provider:",
        choices=PROVIDERS["selectize"],
        selected=selected,
        multiple=False,
    )
    return app_ui


@module.server
def mod_codespace_server(input, output, session):
    return input.codespace


def mod_codespace_app():

    app_ui = ui.page_navbar(
        ui.nav_panel("Test", output_widget("map")),
        sidebar=ui.sidebar(
            mod_codespace_ui("codespace"),
            width=350,
        ),
        fillable=True,
    )

    def server(input, output, session):
        m = Map()
        codespace = mod_codespace_server("codespace")

        @render_widget
        def map():
            return m

        @reactive.effect
        @reactive.event(codespace)
        def set_map_center():
            center = PROVIDERS["centers"].get(codespace())
            if center:
                m.center = [center["longitude"], center["latitude"]]
                m.zoom = center["zoom"]

    return App(app_ui, server)
