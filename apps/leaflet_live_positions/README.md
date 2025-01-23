# Leaflet Live Positions

 Shiny app demonstrating real-time position updates on a map using `ipyleaflet`. The app simulates live flight data with adjustable playback speed and refresh intervals. Users can interact with the map to observe moving markers representing flight positions.

 ## Features
- Real-time flight position simulation
- Adjustable playback speed and refresh intervals
- Interactive map with dynamic markers
- Reset and quick playback controls

## Running the app
```python
shiny run apps.leaflet_live_positions.app
```

## Notes
Note that this requires `shinywidgets<=0.3.4` [[1]](https://github.com/posit-dev/py-shinywidgets/issues/174) and `ipywidgets<=7.7.5` [[2]](https://github.com/posit-dev/py-shinywidgets/issues/101). The `requirements.txt` in this folder is only for shinylive.io compatibility. For local development, use the `requirements.txt` in the root folder. 