from shiny import App, reactive, render, req, ui
from pathlib import Path
import yaml

app_dir = Path(__file__).parent

with open(app_dir / "apps.yaml", "r") as file:
    apps = yaml.safe_load(file)

cards = []
for app in apps.get("apps", []):
    cards.append(
        ui.card(
            ui.card_body(ui.img(src=app["image"]), class_="p-0"),
            ui.card_body(
                ui.h5(app["title"], class_="fw-bold mt-3"),
                ui.markdown(app["body"]),
                ui.a(
                    "Go to app",
                    href=app["link"],
                    target="_blank",
                    class_="btn btn-sm btn-dark stretched-link mt-2",
                ),
                gap=0,
            ),
        )
    )


app_ui = ui.page_fluid(
    ui.head_content(ui.tags.title("Shiny for Python templates")),
    ui.div(
        ui.div(
            ui.h1("Shiny Templates", class_="display-6 fw-bold"),
            ui.markdown(
                """
                A set of personal shiny for python templates available at
                [thohan88/py-shiny-templates](https://github.com/thohan88/py-shiny-templates).
                """
            ),
            class_="text-center",
        ),
        ui.layout_column_wrap(*cards, width=280),
        class_="col-md-10 mx-auto",
    ),
    class_="p-4"
)


def server(input, output, session):
    pass


app = App(app_ui, server, static_assets=app_dir / "www")
