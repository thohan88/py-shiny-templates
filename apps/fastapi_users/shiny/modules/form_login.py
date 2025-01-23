from shiny import App, ui, reactive, module
from shiny.module import resolve_id
from shiny_validate import check, InputValidator
from ...config import settings

LOGIN_FORM_ID = "login_form"
LOGIN_EVENT_ID = "submit_login_form"


@module.ui
def mod_form_login_ui():

    # Trigger form submission after input is validated
    # https://github.com/posit-dev/py-shiny/issues/1770
    js = f"""
        document.addEventListener('DOMContentLoaded', function() {{
            Shiny.addCustomMessageHandler('{resolve_id(LOGIN_EVENT_ID)}', function(message) {{
                document.getElementById('{resolve_id(LOGIN_FORM_ID)}').submit(); 
            }});
        }});
    """

    input_email = ui.input_text(
        id="email",
        label=None,
        autocomplete="email",
        width="100%",
        placeholder="E-mail",
    )
    input_email.children[1].attrs["type"] = "email"
    input_email.children[1].attrs["name"] = "username"

    input_password = ui.input_password(
        id=resolve_id("password"), label=None, width="100%", placeholder="Password"
    )
    input_password.children[1].attrs["name"] = "password"
    input_password.children[1].attrs["autocomplete"] = "current-password"

    app_ui = ui.TagList(
        ui.tags.script(js),
        ui.tags.form(
            input_email,
            input_password,
            ui.input_action_button(
                "login_form_submit",
                "Log in",
                width="100%",
                class_="btn-dark btn-sm",
            ),
            id=resolve_id(LOGIN_FORM_ID),
            action=settings.path_root + "/api/auth/web/login",
            method="POST",
        ),
    )
    return app_ui


@module.server
def mod_form_login_server(input, output, session, api_client, reset_login_form):

    iv = InputValidator()
    iv.add_rule("email", check.required("Please provide a valid e-mail"))
    iv.add_rule("email", check.email("Please provide a valid e-mail"))
    iv.add_rule("password", check.required("Please provide a password"))

    @reactive.Effect
    @reactive.event(input.login_form_submit)
    async def login_form_submit():
        iv.enable()
        if iv.is_valid():
            resp = await api_client.post(
                "/api/auth/validate-credentials",
                data={
                    "username": input.email(),
                    "password": input.password(),
                },
            )
            if resp.status_code == 200:
                await session.send_custom_message(resolve_id(LOGIN_EVENT_ID), {})
            else:
                ui.notification_show("Username/Password not valid")

    @reactive.effect
    def reset_form():
        if reset_login_form():
            ui.update_text("email", value="")
            ui.update_text("password", value="")
            # iv.disable()
            reset_login_form.set(False)


# Run module by running:
# shiny run apps.fastapi_users.shiny.modules.form_login:mod_form_login_app --reload
def mod_form_login_app():
    from ...app import run_app
    from ..client import get_api_client
    app_ui = ui.page_auto(ui.h2("Login", class_="fw-bold"), mod_form_login_ui("login"))

    def server(input, output, session):
        reset_login_form = reactive.value(False)
        api_client = get_api_client(session)
        mod_form_login_server("login", api_client, reset_login_form=reset_login_form)

    return run_app(App(app_ui, server))
