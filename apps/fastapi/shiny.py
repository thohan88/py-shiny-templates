from shiny import App, reactive, render, ui
from shiny.session import get_current_session
import httpx
import os


def app_ui(request):
    app_ui = ui.page_navbar(
        ui.head_content(ui.tags.title("FastAPI Integration")),
        ui.nav_panel(
            "FastAPI Example",
            ui.div(
                ui.h1("FastAPI Example", class_="fw-bold"),
                ui.p(
                    "A minimal example to show how FastAPI and Shiny can work together."
                ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Multiply"),
                        ui.input_slider("n", "N", 0, 100, 20),
                        ui.output_text_verbatim("txt"),
                    ),
                    ui.card(
                        ui.card_header("Hello world"),
                        ui.div(
                            ui.input_action_button(
                                "btn", label="Hello world", class_="btn-primary"
                            ),
                            class_="d-flex align-items-center justify-content-center h-100",
                        ),
                    ),
                ),
                ui.card(
                    ui.card_header(ui.a("Docs", href="api/docs")),
                    ui.tags.iframe(src="api/docs", height=600),
                ),
                class_="col-md-6 mx-auto",
            ),
        ),
        underline=False,
    )
    return app_ui


def server(input, output, session):

    def get_base_url(session):
        # Use ClientData to get URL components to build the base url.
        # These values are from the browser's perspective, so neither
        # HTTP proxies nor Shiny Server will affect these values.
        # Seems to be the most reliable method of solving subpaths etc.
        # Wrap in isolate to avoid taking a reactive dependency.
        # See ClientData section in the documentation:
        # https://shiny.posit.co/r/reference/shiny/latest/session.html
        with reactive.isolate():
            protocol = session.input[".clientdata_url_protocol"]()
            hostname = session.input[".clientdata_url_hostname"]()
            pathname = session.input[".clientdata_url_pathname"]()
            port = session.input[".clientdata_url_port"]()

        if port:
            url = f"{protocol}//{hostname}:{port}{pathname}"
        else:
            url = f"{protocol}//{hostname}{pathname}"

        return url

    session = get_current_session()
    base_url = get_base_url(session)
    api_client = httpx.AsyncClient(base_url=base_url, verify=False)


    @render.text
    async def txt():
        resp = await api_client.get("api/multiply", params={"n": input.n()})
        return resp.json().get("result")


    @reactive.effect
    @reactive.event(input.btn)
    async def _():
        resp = await api_client.get("api/hello_world")
        ui.modal_show(ui.modal(resp.json().get("message"), easy_close=True))


app = App(app_ui, server)
