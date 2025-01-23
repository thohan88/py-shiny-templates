from shiny import module, ui, App, reactive, render
from shiny_validate import InputValidator, check
from ...config import settings


@module.ui
def mod_form_register_ui():

    app_ui = ui.div(
        ui.input_text(
            id="email",
            label=None,
            placeholder="E-mail",
            width="100%",
        ),
        ui.input_password(
            id="password", label=None, placeholder="Password", width="100%"
        ),
        ui.input_action_button(
            "submit",
            "Register",
            width="100%",
            class_="btn-dark btn-sm",
        ),
    )
    return app_ui


@module.server
def mod_form_register_server(input, output, session, api_client, reset_register_form):
    registered_username = reactive.Value(None)

    iv = InputValidator()
    iv.add_rule("email", check.required("Please provide a valid e-mail"))
    iv.add_rule("email", check.email("Please provide a valid e-mail"))
    iv.add_rule("password", check.required("Please provide a password"))

    @reactive.effect
    @reactive.event(input.submit)
    async def _():
        iv.enable()
        if iv.is_valid():
            data = {"email": input.email(), "password": input.password()}

            response = await api_client.post("/api/auth/register", json=data)

            if response.status_code == 201:
                ui.notification_show(
                    ui.TagList(
                        ui.h5(f"Registration successful", class_="fw-bold"),
                        ui.p(
                            f"Succesfully registered {input.email()}",
                            class_="text-muted",
                        ),
                    )
                )
                ui.update_text("email", value="")
                ui.update_text("password", value="")
                registered_username.set(input.email())
                iv.disable()

            else:
                result = f"Registration failed: {response.text}"
                ui.notification_show(
                    ui.TagList(
                        ui.h5(f"Registration failed", class_="fw-bold"),
                        ui.p(result, class_="text-muted"),
                    )
                )

    @reactive.effect
    def reset_form():
        if reset_register_form():
            ui.update_text("email", value="")
            ui.update_text("password", value="")
            #iv.disable()
            reset_register_form.set(False)

    return registered_username

# Run module by running:
# shiny run apps.fastapi_users.shiny.modules.form_register:mod_form_register_app --reload
def mod_form_register_app():
    from ...app import run_app
    from ..client import get_api_client
    app_ui = ui.page_auto(
        ui.div(
            ui.navset_pill(
                ui.nav_panel("Register", mod_form_register_ui("register")),
                ui.nav_panel("Login", "Login page"),
                id="navbar_tabs"
            ),
        )
    )

    def server(input, output, session):
        api_client = get_api_client(session)
        reset_register_form = reactive.value(False)
        registered_username = mod_form_register_server("register", api_client, reset_register_form)

        @reactive.effect
        def user_registered():
            if registered_username() is not None:
                ui.update_navs("navbar_tabs", selected="Login")
    
    app = run_app(App(app_ui, server))

    return app
