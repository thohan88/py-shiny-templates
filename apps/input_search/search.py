from __future__ import annotations
from shiny.session import require_active_session, Session
from shiny.types import Jsonifiable
from shiny.ui import input_selectize
from shiny.ui._utils import JSEval, extract_js_keys
from shiny._utils import drop_none
from typing import Any, Callable, Optional
from htmltools import TagList, TagChild, Tag, tags
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import json


def input_search(
    id: str,
    label: TagChild = None,
    *,
    multiple: bool = False,
    width: Optional[str] = None,
    remove_button: Optional[bool] = None,
    options: Optional[dict[str, Jsonifiable | JSEval]] = None,
    ) -> Tag:
    return input_selectize(
        id = id,
        label = label,
        choices = [],
        multiple = multiple,
        width = width,
        remove_button = remove_button,
        options = options
    )


def update_search(
    id: str,
    *,
    label: Optional[str] = None,
    selected: Optional[str | list[str]] = None,
    options: Optional[dict[str, str | float | JSEval]] = None,
    session: Optional[Session] = None,
    search_func: Callable[..., Any],  # A function to retrieve results from server side
    **kwargs  # Arbitrary keyword arguments (e.g. database conenction)
    ) -> None:

    session = require_active_session(session)

    if options is not None:
        cfg = TagList(
            tags.script(
                json.dumps(options),
                type="application/json",
                data_for=id,
                data_eval=json.dumps(extract_js_keys(options)),
            )
        )
        session.send_input_message(id, drop_none({"config": cfg.get_html_string()}))

    # Function to handle dynamic search requests
    def selectize_choices_json(request: Request) -> Response:        
        search_query = request.query_params.get("query", "")
        # Pass any arbitrary `kwargs` (e.g., connection, filters) to search_func
        search_result = search_func(search_query, **kwargs)

        return JSONResponse(search_result, status_code=200)

    msg = {
        "label": label,
        "value": selected,
        "url": session.dynamic_route(f"update_selectize_{id}", selectize_choices_json),
    }

    return session.send_input_message(id, drop_none(msg))
