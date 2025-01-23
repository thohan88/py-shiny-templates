from shiny import module, reactive, render, ui, App
from .live import mod_live_server
import plotly.express as px
import json
from shinywidgets import output_widget, render_plotly, render_widget
import pandas as pd


@module.ui
def mod_stats_ui():
    app_ui = ui.TagList(
        ui.value_box(
            ui.TagList(
                ui.div(
                    ui.tags.strong(ui.output_text("messages_last_second", inline=True)),
                    " messages per second",
                ),
                ui.div(
                    ui.tags.strong(ui.output_text("messages_total", inline=True)),
                    " messages total",
                ),
            ),
            None,
            height=170,
            showcase=output_widget("message_sparkline", width="400px"),
            showcase_layout="bottom",
        ),
        ui.value_box(
            ui.TagList(
                ui.div(
                    ui.tags.strong(ui.output_text("vehicles_last_second", inline=True)),
                    " positions per second",
                ),
                ui.div(
                    ui.tags.strong(ui.output_text("vehicles_total", inline=True)),
                    " positions total",
                ),
            ),
            None,
            height=170,
            showcase=output_widget("vehicle_sparkline", width="400px"),
            showcase_layout="bottom",
        ),
    )
    return app_ui


@module.server
def mod_stats_server(input, output, session, data):


    def render_plot(df):
        fig = px.line(df, x="datetime", y="n")
        fig.update_traces(
            line_color="#406EF1",
            line_width=1,
            fill="tozeroy",
            fillcolor="rgba(64,110,241,0.2)",
            hovertemplate="Time: %{x|%H:%M:%S}<br>Value: %{y}<extra></extra>",
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

    @reactive.calc
    def data_available():
        return data() is not None and not data().empty

    @render.text
    def messages_last_second():
        return str(data()["messages_last_second"][0]) if data_available() else "0"

    @render.text
    def messages_total():
        return str(data()["messages_total"][0]) if data_available() else "0"

    @render.text
    def vehicles_last_second():
        return str(data()["vehicles_last_second"][0]) if data_available() else "0"

    @render.text
    def vehicles_total():
        return str(data()["vehicles_total"][0]) if data_available() else "0"

    @render_widget
    def message_sparkline():
        if data_available():
            df = pd.DataFrame(json.loads(data()["messages_per_second"][0])).sort_values(
                "datetime"
            )
        else:
            df = pd.DataFrame(columns=["datetime", "n"])
        return render_plot(df)

    @render_widget
    def vehicle_sparkline():
        if data_available():
            df = pd.DataFrame(json.loads(data()["vehicles_per_second"][0])).sort_values(
                "datetime"
            )
        else:
            df = pd.DataFrame(columns=["datetime", "n"])
        return render_plot(df)


def mod_stats_app():

    app_ui = ui.page_navbar(
        ui.nav_panel("Test", ""),
        sidebar=ui.sidebar(
            ui.input_select(
                "codespace_id", "Codespace", choices=["SKY", "ALL"], selected="ALL"
            ),
            ui.input_switch("get_live_data", "Get live data", True),
            mod_stats_ui("live"),
            width=350,
        ),
    )

    def server(input, output, session):

        data = mod_live_server("live", input.get_live_data, input.codespace_id)
        mod_stats_server("live", data)

    return App(app_ui, server)
