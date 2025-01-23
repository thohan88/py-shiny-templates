from shiny import ui, App, module
from shiny.module import resolve_id
from ...config import settings


@module.ui
def mod_button_logout_ui(
    form_id="logoutForm", button_id="logoutSubmit", class_="btn btn-sm"
):

    form_id = resolve_id(form_id)
    button_id = resolve_id(button_id)

    # Necessary to be able to submit form using POST
    # https://github.com/posit-dev/py-shiny/issues/1770
    js = f"""
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById("{resolve_id(button_id)}").addEventListener('click', function(event) {{
                document.getElementById("{resolve_id(form_id)}").submit();
            }});
        }});
        """

    form = ui.TagList(
        ui.tags.script(js),
        ui.tags.form(
            ui.tags.button(
                "Log out",
                type="submit",
                id=button_id,
                class_="btn btn-sm btn-dark",
            ),
            id=form_id,
            action=settings.path_root + "/api/auth/web/logout",
            method="POST",
        ),
    )

    return form


@module.server
def mod_button_logout_server(input, output, session):
    pass


# Run module by running:
# shiny run apps.fastapi_users.shiny.modules.button_logout:mod_button_logout_app --reload
def mod_button_logout_app():
    from ...app import run_app
    app_ui = ui.page_auto(ui.div(mod_button_logout_ui("logout_button")))

    def server(input, output, session):
        mod_button_logout_server("logout_button")

    app = run_app(App(app_ui, server))
    return app
