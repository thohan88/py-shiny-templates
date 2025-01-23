from shiny import module, reactive, ui, App, req, render
from ..database.database import create_sqlite_db, delete_sqlite_db, con_duckdb
from ..client import vehicle_websocket_client
import time


@module.server
def mod_live_server(input, output, session, trigger, codespace_id, verbose=False):

    # We are utilizing two databases:
    # 1) A sqlite database for quick async writes
    # 2) A duckdb database which reads to attached sqlite
    # Need to make sure sqlite (1) is created before accessing (2)
    db_sqlite_created = reactive.value(False)

    @reactive.effect
    async def set_db_sqlite_created():
        await create_sqlite_db()
        db_sqlite_created.set(True)

    @reactive.calc
    def duckdb():
        if db_sqlite_created():
            return con_duckdb()

    def data():
        if duckdb():
            if trigger():
                reactive.invalidate_later(1)

        # Simple retry logic to handle occasional i/o errors
        retries = 3 
        for attempt in range(retries):
            try:
                df = duckdb().execute("FROM GET_DATA(?)", [codespace_id()]).df()
                return df
            except Exception as e:
                if attempt == retries - 1: 
                    raise  
                time.sleep(0.1)  

    @reactive.extended_task
    async def connect_to_websocket(codespace_id):
        await vehicle_websocket_client(codespace_id=codespace_id, verbose=verbose)

    @reactive.effect
    @reactive.event(trigger, codespace_id)
    def handle_switch():
        if trigger():
            connect_to_websocket.cancel()
            connect_to_websocket(codespace_id())
        else:
            connect_to_websocket.cancel()

    @reactive.effect
    @reactive.event(trigger)
    def handle_switch():
        if trigger() and db_sqlite_created():
            connect_to_websocket(codespace_id())
        else:
            connect_to_websocket.cancel()

    def exit():
        connect_to_websocket.cancel()
        delete_sqlite_db()

    session.on_ended(exit)

    return data


def mod_live_app():
    from .codespace import mod_codespace_server, mod_codespace_ui
    import json

    app_ui = ui.page_fluid(
        ui.input_switch("get_live_data", "Get live data", True),
        mod_codespace_ui("codespace"),
        ui.span("Vehicles per second:"),
        ui.output_text_verbatim("vehicles", placeholder=True)
    )

    def server(input, output, session):
        codespace_id = mod_codespace_server("codespace")
        data = mod_live_server("live", input.get_live_data, codespace_id)

        @render.text
        def vehicles():
            req(data() is not None and not data().empty)
            return str(data()["vehicles_last_second"][0]) + " vehicles"

    return App(app_ui, server)
