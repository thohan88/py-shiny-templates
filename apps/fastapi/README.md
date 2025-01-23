# FastAPI Integration Example

A minimal example demonstrating the integration of FastAPI and Shiny. The app consists of a FastAPI backend mounted at `/api` and a Shiny frontend that communicates with the API endpoints.

## Features
- FastAPI endpoints for basic operations (hello world, multiplication)
- Interactive Shiny UI with slider inputs and buttons
- Automatic Swagger documentation at `/api/docs`
- Async communication between Shiny and FastAPI


## Running the app

``` bash
shiny run apps.fastapi.app
```
