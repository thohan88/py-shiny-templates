from shiny import App, reactive, render, req, ui
from .modules.button_logout import mod_button_logout_ui


app_ui = ui.page_navbar(
    ui.head_content(ui.tags.title("FastAPIUsers integration")),
    ui.nav_panel(
        "Info",
        ui.div(
            ui.markdown(
                """
            ### **FastAPI + FastAPIUsers + Shiny**
            This app shows how [FastAPI](https://github.com/fastapi/fastapi) 
            and [FastAPIUsers](https://github.com/fastapi-users/fastapi-users) 
            can be used together with Shiny. FastAPIUsers is an extension 
            that allows you to quickly add registration and authentication 
            to an application. The setup is based on the [examples](https://fastapi-users.github.io/fastapi-users/14.0/configuration/full-example/) in the FastAPIUsers documentation, with some custom 
            auth middleware for Starlette.
            """
            ),
            ui.div(
                ui.p(
                    ui.markdown(
                        """
                        #### **Disclaimer**  
                        This example is a work in progress and is provided as-is for 
                        illustrative purposes only. It has not been thoroughly tested 
                        or validated for production use. Use it at your own risk. The 
                        author assumes no responsibility for any issues, including 
                        security vulnerabilities, performance problems, or other 
                        unexpected behavior that may arise from its use.
                        """
                    )
                ),
                class_="alert alert-light pt-0 pb-0",
            ),
            ui.markdown(
                """
                This example uses cookie-based authentication with JWT to gate 
                access to the app. Users are stored in a local SQLite database 
                based on the environment variable `DB_URL`.
                """
            ),
            class_="col-md-8 mx-auto mt-5",
        ),
    ),
    ui.nav_panel("Docs", ui.tags.iframe(src="api/docs", height="100%", width="100%")),
    ui.nav_spacer(),
    ui.nav_control(
        ui.div(
            mod_button_logout_ui("logout_navbar"),
            class_="d-flex align-items-center justify-content-center h-100",
        ),
    ),
    fillable=True,
    fillable_mobile=True
)


def server(input, output, session):
    pass


app = App(app_ui, server)
