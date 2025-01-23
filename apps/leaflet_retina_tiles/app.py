from shiny import ui, App, reactive
from ipyleaflet import Map, TileLayer, basemaps, basemap_to_tiles, SplitMapControl
from shinywidgets import output_widget, render_widget
from pathlib import Path

app_ui = ui.page_fillable(
    ui.head_content(ui.tags.title("Leaflet retina tiles")),
    ui.head_content(
        ui.tags.style(
            """ 
            .bslib-page-fill {padding: 0 !important;}
            .jupyter-widgets {margin: 0 !important;}
            .map-inputs {z-index:1000 !important;}
            """
        ),
    ),
    output_widget("map"),
    ui.panel_absolute(
        ui.card(
            ui.card_body(
                ui.markdown(
                    """
                    ###### **Retina tiles**
                    For use in `pyleaflet`:
                    ```python
                    TileLayer(
                        name="Basemap",
                        tile_size=512,
                        zoom_offset=-1,
                        detect_retina=True,
                        url="https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                    )
                    ``` 
                    """
                ),
                gap=0,
            ),
            gap=0,
        ),
        width="200px",
        top="10px",
        right="10px",
        draggable=False,
        class_="map-inputs small",
    ),
    fillable_mobile=True,
)


def server(input, output, session):

    layer_non_retina = basemap_to_tiles(basemaps.CartoDB.Positron)

    layer_retina = TileLayer(
        name="Basemap",
        tile_size=512,
        zoom_offset=-1,
        detect_retina=True,
        url="https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
    )

    split_light = SplitMapControl(left_layer=layer_retina, right_layer=layer_non_retina)

    m = Map(center=(59.95, 10.74), zoom=10)
    m.add_control(split_light)

    @output
    @render_widget
    def map():
        return m


app = App(app_ui, server)
