from shiny import ui, App, module, render
from ...config import settings

SVG_ICON = """
    <svg height="15" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" xmlns:xlink="http://www.w3.org/1999/xlink" style="display: block;">
       <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
       <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
       <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
       <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
       <path fill="none" d="M0 0h48v48H0z"></path>
    </svg>
    """


@module.ui
def mod_button_google_ui():
    return ui.output_ui("google_login_link")


@module.server
def mod_button_google_server(input, output, session, api_client, title="Google"):

    @render.ui()
    async def google_login_link():
        link = ui.tags.a(
            ui.HTML(SVG_ICON),
            title,
            class_="btn btn-light btn-sm d-flex align-items-center justify-content-center gap-2",
        )
        if settings.google_client_id and settings.google_client_secret:
            response = await api_client.get("/api/auth/google/authorize")
            href = response.json().get("authorization_url")
            link.attrs["href"] = href
        else:
            # Disable but keep link if env vars not set
            link.add_class("disabled")
            link.attrs["href"] = "#"
            link = ui.popover(
                ui.span(link, tabindex="0"),
                ui.markdown(
                    """
                    To use Google, you need to provide the following
                    variables in `.env`
                    - `GOOGLE_CLIENT_ID`
                    - `GOOGLE_CLIENT_SECRET`

                    Rename the provided `.env.example` to `.env` and 
                    provide the required variables. This requires you to
                    setup a Google project with
                    [OAuth2.0](https://support.google.com/cloud/answer/6158849?hl=en#zippy=). 
                    Remember also to:
                    - Enable People API in Console
                    - Set your callback in Console: `/api/auth/google/callback`
                    """
                ),
                title="Environment variables required",
                placement="right"
            )

        return link


# Run module by running:
# shiny run apps.fastapi_users.shiny.modules.button_google:mod_button_google_app --reload
def mod_button_google_app():
    from ...app import run_app
    from ..client import get_api_client

    app_ui = ui.page_fluid(mod_button_google_ui("logout_button"))

    def server(input, output, session):
        api_client = get_api_client(session)
        mod_button_google_server("logout_button", api_client)

    app = run_app(App(app_ui, server))
    return app

