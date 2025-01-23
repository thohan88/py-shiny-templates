from shiny import App, reactive, render, ui
from .client import get_api_client
from .modules.form_login import mod_form_login_ui, mod_form_login_server
from .modules.form_register import mod_form_register_ui, mod_form_register_server
from .modules.button_google import mod_button_google_ui, mod_button_google_server

disclaimer = ui.markdown(
    """
    This app is for illustration purposes. It uses a SQLite database which is reset between sessions.
    Use a fictitious username and password to ensure privacy.
    """
)

app_ui = ui.page_fluid(
    ui.head_content(ui.tags.title("FastAPIUsers example")),
    ui.div(
        ui.navset_hidden(
            ui.nav_panel(
                "Login",
                ui.div(
                    ui.h5("Login", class_="fw-bold text-center"),
                    ui.p(
                        "Enter your email and password to log in",
                        class_="text-muted text-center",
                    ),
                    ui.div(mod_form_login_ui("login")),
                    ui.p(
                        "or continue with",
                        class_="text-muted text-center small m-0 mt-1 mb-1",
                    ),
                    mod_button_google_ui("google_login_link"),
                    ui.div(
                        ui.p("Don't have an account?", class_="text-muted m-0 me-1"),
                        ui.input_action_button(
                            "register_tab",
                            "Signup now",
                            class_="btn-sm btn-link p-0 text-muted",
                        ),
                        class_="d-flex justify-content-center align-items-center mt-1 small",
                    ),
                    ui.div(
                        disclaimer,
                        class_="mt-2 text-muted text-center small",
                    ),
                    style="width: 350px;",
                ),
            ),
            ui.nav_panel(
                "Register",
                ui.div(
                    ui.h5("Create account", class_="fw-bold text-center"),
                    ui.p(
                        "Enter your email below to create your account",
                        class_="text-muted text-center",
                    ),
                    ui.div(mod_form_register_ui("register")),
                    ui.p(
                        "or register with",
                        class_="text-muted text-center small m-0 mt-1 mb-1",
                    ),
                    mod_button_google_ui("google_register_link"),
                    ui.div(
                        ui.p("Already have an account?", class_="text-muted m-0 me-1"),
                        ui.input_action_button(
                            "login_tab",
                            "Login now",
                            class_="btn-sm btn-link p-0 text-muted",
                        ),
                        class_="d-flex justify-content-center align-items-center mt-1 small",
                    ),
                    ui.div(
                        disclaimer,
                        class_="mt-2 text-muted text-center small",
                    ),
                    style="width:350px;",
                ),
            ),
            id="login_register",
        ),
        class_="d-flex justify-content-center align-items-center vh-100",
    ),
)


def server(input, output, session):

    reset_login_form = reactive.value(None)
    reset_register_form = reactive.value(None)

    api_client = get_api_client(session)

    mod_form_login_server("login", api_client, reset_login_form)
    registered_user = mod_form_register_server(
        "register", api_client, reset_register_form
    )
    mod_button_google_server("google_login_link", api_client)
    mod_button_google_server("google_register_link", api_client)

    @reactive.effect
    def user_registered():
        if registered_user() is not None:
            ui.update_navs("login_register", selected="Login")

    @reactive.effect()
    @reactive.event(input.login_tab)
    def navigate_to_login():
        ui.update_navs("login_register", selected="Login")
        reset_register_form.set(True)

    @reactive.effect()
    @reactive.event(input.register_tab)
    def navigate_to_register():
        ui.update_navs("login_register", selected="Register")
        reset_login_form.set(True)


app = App(app_ui, server)
