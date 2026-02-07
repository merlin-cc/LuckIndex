# LuckIndex — Web application

LuckIndex is a small Flask web application to visualize and analyze a "luck index" computed for tournament draws in Tennis and Football.


Summary
- Purpose: simulate tournament draws and compute a luck score for players (tennis) or teams (football), helping to quantify how "lucky" a given draw was compared to simulation-based expectations.
- Tech stack: Python, Flask, Pandas, Matplotlib.


Key features
- Web UI with separate Tennis and Football tabs.
- Configurable number of simulations fot the tennis mode (default examples use 10,000).
- Multiple draw modes: random/manual (tennis), official draw/random (football).


User interface:
- Tennis tab: choose a mode (Random or Manual), select players when using Manual mode, set the number of simulations, and view generated plots and the computed luck-index results.
- Football tab: choose between the official 2026 World Cup draw or a random draw, set the number of simulations, and view the draw image, distributions and luck-index charts.


Notes
- Plots are generated with Matplotlib on the server and encoded to Base64 to be embedded in the HTML template; the app switches Matplotlib to the `Agg` backend for headless rendering.
- The application expects CSV ranking files present under `Tennis/` and `Football/` directories.