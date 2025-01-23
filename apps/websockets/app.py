from shiny import App, reactive, render, ui
from .modules.codespace import mod_codespace_server, mod_codespace_ui
from .modules.map import mod_map_server, mod_map_ui
from .modules.live import mod_live_server
from .modules.stats import mod_stats_server, mod_stats_ui
from pathlib import Path

app_ui = ui.page_fillable(
    ui.head_content(
        ui.include_css(Path(__file__).parent / "styles.css"),
        ui.tags.title("Websockets dashboard"),
    ),
    ui.layout_sidebar(
        ui.sidebar(
            mod_codespace_ui("codespace").add_class("m-0 p-0"),
            ui.input_switch("get_live_data", "Get live data", True),
            mod_stats_ui("stats"),
            ui.tags.small(
                ui.markdown(
                """
                This is a real-time dashboard based on a websockets API of 
                [vehicle positions](https://developer.entur.org/pages-real-time-vehicle)
                from the Norwegian transportation company [Entur](https://entur.no/).
                """
                )
            ),
            width=350,
            
        ),
        mod_map_ui("map"),
    ),
    fillable=True,
    fillable_mobile=True,
)


def server(input, output, session):
    codespace_id = mod_codespace_server("codespace")
    data = mod_live_server("live", input.get_live_data, codespace_id)
    mod_map_server("map", codespace_id, data)
    mod_stats_server("stats", data)

    @reactive.effect
    @reactive.event(codespace_id, ignore_init=True)
    def show_provider_change_notification():
        ui.notification_show(
            ui.TagList(
                ui.p("Changing providers", class_="fw-bold"),
                ui.p("This may take a couple of seconds"),
            )
        )


app = App(app_ui, server)
