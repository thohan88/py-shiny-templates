from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

# Ugly fix for deploying to shinyapps (behind reverse proxy)
# 
# Override docs url as fastapi does not know it's mounted in app.py
# Setting up root_url should be the preferred way of going about
# this, but is currently a mess in fastapi/starlette/uvicorn. 
# https://github.com/fastapi/fastapi/pull/11160
# https://github.com/fastapi/fastapi/discussions/11033#discussioncomment-8546202
# https://github.com/fastapi/fastapi/discussions/11977
#
# So instead of doing app=FastAPI(), we end up with the below

app = FastAPI(docs_url=None, servers=[{'url': './'}], root_path_in_servers=False)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="openapi.json",
        title="Docs"
    )

@app.get("/hello_world")
async def hello_world():
    return {"message": "Hello World from FastAPI"}

@app.get("/multiply")
async def multiply(n: int):
    return {"result": f"n * 2 is {n * 2}"}
