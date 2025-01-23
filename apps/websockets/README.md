# Websockets Example

A real-time dashboard built using websockets to stream vehicle positions from the Norwegian transportation company Entur. The app visualizes live data on a map and provides statistics on message and vehicle activity. At rush hours, `>1000` vehicle positions are streaming in per second.

## Running the App
```bash
shiny run apps.websockets.app
```

## Notes
Requires a `.env` file with `entur_wss_url` and `entur_wss_client_name` for websocket connection. These are not API keys but [affiliations](https://developer.entur.org/pages-intro-authentication). Entur may enforce rate limiting if they are missing. See API-documentation [here](https://developer.entur.org/pages-real-time-vehicle)