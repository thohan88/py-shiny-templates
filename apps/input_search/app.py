from shiny import ui, App, reactive, render
from .search import input_search, update_search
from .search_database import duckdb_connect, get_search_result_db
from .search_api import get_search_result_api
import os
import json

DB_PATH = "cities.db"

display_search_choices = ui.js_eval(
    """
    {
        option: function(item, escape) {
            return `
                <div class="px-3 py-1 border-bottom">
                    <span class="d-block small">
                        ${escape(item.label)}
                        <div class = "small text-muted">
                            ${escape(item.zipCode)} ${escape(item.zipName)}
                        </span>
                    </span>
                </div>
            `;
        }
    }
    """
)

app_ui = ui.page_auto(
    ui.head_content(
        ui.tags.style(".card, .card-body {overflow: visible !important;}"),
        ui.tags.title("Server side search"),
    ),
    ui.div(
        ui.h1("Server side search", class_="fw-bold text-center"),
        ui.markdown(
            """
            Shiny includes a built-in server-side selectize component that stores
            data on the server, which works well for medium-sized datasets. However,
            this approach can become memory-intensive when handling larger datasets.
            
            This app tweaks `ui.input_selectize()` and allows you to to pass a custom
            function for dynamically select choices. This enables integration with any
            back-end, such as databases or APIs, making it ideal for search bars, 
            data validation, and other features while maintaining a low memory footprint.
            """
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header("Database search"),
                ui.card_body(
                    ui.div(
                        ui.markdown("**47 605** cities"),
                        class_="small text-muted text-center",
                    ),
                    input_search(
                        "search_db", multiple=False, remove_button=True, width="100%"
                    ),
                    ui.output_ui("city_info"),
                    gap=1,
                ),
            ),
            ui.card(
                ui.card_header("API search"),
                ui.card_body(
                    ui.div(
                        ui.markdown("**~2.5 million** addresses"),
                        class_="small text-muted text-center",
                    ),
                    input_search(
                        "search_api", multiple=False, remove_button=True, width="100%"
                    ),
                    ui.input_text(
                        "addressText", label=None, placeholder="Street", width="100%"
                    ).add_class("mt-3"),
                    ui.input_text(
                        "zipCode", label=None, placeholder="Zip Code", width="100%"
                    ).add_class("mt-1"),
                    ui.input_text(
                        "zipName", label=None, placeholder="Zip Region", width="100%"
                    ).add_class("mt-1"),
                    gap=1,
                ),
            ),
        ),
        class_="col-10 mx-auto mt-5",
    ),
)


def server(input, output, session):

    con = duckdb_connect(DB_PATH)

    ##################################
    # Search API ----
    ##################################

    # Update address search result from API
    update_search(
        "search_api",
        options={
            "placeholder": "Search",
            "render": display_search_choices,
            "highlight": False,
            "searchField": ["label", "municipality", "zipName"],
            "sortField": [
                {"field": "addressName", "direction": "asc"},
                {"field": "addressNumber", "direction": "asc"},
                {"field": "addressLetter", "direction": "asc"},
                {"field": "$score"},
            ],
        },
        search_func=get_search_result_api,
    )

    @reactive.effect
    @reactive.event(input.search_api)
    def update_forms():
        if input.search_api():
            data = json.loads(input.search_api())
            ui.update_text("addressText", value=data["addressText"])
            ui.update_text("zipCode", value=data["zipCode"])
            ui.update_text("zipName", value=data["zipName"])
        else:
            ui.update_text("addressText", value="")
            ui.update_text("zipCode", value="")
            ui.update_text("zipName", value="")

    ##################################
    # Search DB ----
    ##################################

    selected_city_data = reactive.Value(None)

    # Update city search results from DB
    update_search(
        "search_db",
        options={"placeholder": "Search", "highlight": False},
        search_func=get_search_result_db,
        con=con,
    )

    @reactive.effect
    @reactive.event(input.search_db)
    def set_selected_city_data():
        selected_city = input.search_db()
        if selected_city:
            data = con.execute(
                "FROM cities WHERE city = ? ORDER BY population DESC LIMIT 1",
                [selected_city],
            ).df()
            selected_city_data.set(data)
            # Reset the search field when the reactive val is set
            # Search bars do not normally keep the query on naivgation
            ui.update_selectize("search_db", selected="")

    @output
    @render.ui
    def city_info():
        # Display some info about the selected city
        if selected_city_data() is not None:
            city = selected_city_data()["city"][0]
            country = selected_city_data()["country"][0]
            population = f'{selected_city_data()["population"][0]:,}'

            return ui.div(
                ui.tags.h5(city, class_="fw-bold"),
                ui.div(f"Country: {country}", class_="small text-muted"),
                ui.div(f"Population: {population}", class_="small text-muted"),
                class_="bg-light text-center py-4 mt-3",
            )
        else:
            return ui.div(
                "Search result displays here", class_="bg-light text-center py-5 mt-3"
            )

    def exit():
        con.close()
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    session.on_ended(exit)


app = App(app_ui, server)
