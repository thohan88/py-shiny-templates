from shiny import App, reactive, render, req, ui
from shinywidgets import render_widget, output_widget
from ipyleaflet import Map, TileLayer, basemaps, basemap_to_tiles
import plotly.express as px
import pandas as pd

theme = ui.Theme.from_brand(__file__)

# Some hardcoded data for value boxes
data = pd.DataFrame(
    {
        "date": [
            "2023-01-01",
            "2023-02-01",
            "2023-03-01",
            "2023-04-01",
            "2023-05-01",
            "2023-06-01",
            "2023-07-01",
            "2023-08-01",
            "2023-09-01",
            "2023-10-01",
        ],
        "values": [10, 12, 8, 11, 9, 13, 14, 10, 15, 12],
    }
)


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def create_value_box_plot(mode, data=data):
    gradient_color = (
        theme.brand.color.palette.get("dark_theme_valuebox_gradient_color")
        if mode == "dark"
        else theme.brand.color.palette.get("valuebox_gradient_color")
    )
    gradient_low = hex_to_rgba(gradient_color, 0)
    gradient_high = hex_to_rgba(gradient_color, 1)

    fig = px.line(data, x="date", y="values", labels={"x": "Date", "y": "Values"})
    fig.update_traces(
        line_color=gradient_high,
        line_width=1,
        fill="tozeroy",
        fillgradient=dict(
            type="vertical", colorscale=[(0.0, gradient_low), (1.0, gradient_high)]
        ),
        hoverinfo="y",
    )

    fig.update_xaxes(visible=False, showgrid=False)
    fig.update_yaxes(visible=False, showgrid=False)
    fig.update_layout(
        height=100,
        hovermode="x",
        margin=dict(t=0, r=0, l=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return fig


app_ui = ui.page_navbar(
    ui.nav_panel(
        "Example",
        ui.layout_columns(
            ui.TagList(
                ui.card(
                    ui.h2("Dark theme example", class_="fw-bold"),
                    ui.p(
                        "Dark theme styling using _brand.yml for logo, leaflet and valueboxes"
                    ),
                ),
                ui.value_box(
                    "Valuebox 1",
                    "2.18 units",
                    showcase=output_widget("valuebox_1"),
                    showcase_layout="bottom",
                    fill=True,
                ),
                ui.value_box(
                    "Valuebox 2",
                    "1.32 units",
                    showcase=output_widget("valuebox_2"),
                    showcase_layout="bottom",
                    fill=True,
                ),
            ),
            output_widget("map"),
        ),
    ),
    ui.nav_spacer(),
    ui.nav_control(
        ui.div(
            ui.input_dark_mode(id="mode", mode="dark"),
            class_="d-flex align-items-center justify-content-center h-100",
        )
    ),
    title=ui.TagList(
        ui.div(
            ui.HTML(theme.brand.logo.small.path.absolute().read_text()),
            ui.span("Dark theme", class_="ms-3"),
            class_="navbar-logo",
        ),
    ),
    theme=theme,
    fillable=True,
    underline=False,
)


def server(input, output, session):
    layer_light = basemap_to_tiles(basemaps.CartoDB.Positron)
    layer_dark = basemap_to_tiles(basemaps.CartoDB.DarkMatter)
    m = Map(center=(59.95, 10.76), zoom=10, layers=[layer_light, layer_dark])

    @render_widget
    def map():
        return m

    @reactive.Effect
    @reactive.event(input.mode)
    def _():
        if input.mode() == "dark":
            layer_light.visible = False
            layer_dark.visible = True
        else:
            layer_dark.visible = False
            layer_light.visible = True

    @render_widget
    def valuebox_1():
        return create_value_box_plot(input.mode())

    @render_widget
    def valuebox_2():
        return create_value_box_plot(input.mode())


app = App(app_ui, server)
