"""
Standalone Dash application for Shooter Game Stat Analyser.

Usage:
    python app.py               # Run with native desktop window (requires pywebview)
    python app.py --browser     # Run in browser only (no pywebview dependency)

Both modes support runtime data reload via the "Reload Data" button.
"""
import sys
import time

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, ctx, dcc, html, no_update

import weaponData as wd

# ---------------------------------------------------------------------------
# Dash app
# ---------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Shooter Game Stat Analyser"

# Build initial weapon name list
weapon_options = [{"label": w.name, "value": w.name} for w in wd.weapons]

app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(html.H3("Shooter Game Stat Analyser", className="mt-3 mb-3")),
        ),
        # Controls row
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id="weaponsDropdown", options=weapon_options, placeholder="Select Weapon"), width=3),
                dbc.Col(
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Toggle", id="toggleVisibility", color="primary", outline=True),
                            dbc.Button("Show All", id="showAll", color="success", outline=True),
                            dbc.Button("Clear All", id="clearAll", color="danger", outline=True),
                        ],
                        size="sm",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button("Reload Data", id="reloadData", color="warning"),
                    width="auto",
                ),
                dbc.Col(
                    html.Span(id="reloadStatus", className="text-muted small align-self-center"),
                    width="auto",
                ),
            ],
            className="mb-3 align-items-center",
        ),
        # Graph
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id="graph",
                    figure=wd.getMasterFigure(hide=True),
                    style={"height": "75vh"},
                ),
            ),
        ),
    ],
    fluid=True,
)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(
    Output("graph", "figure"),
    Output("weaponsDropdown", "options"),
    Output("weaponsDropdown", "value"),
    Output("reloadStatus", "children"),
    Input("toggleVisibility", "n_clicks"),
    Input("weaponsDropdown", "value"),
    Input("showAll", "n_clicks"),
    Input("clearAll", "n_clicks"),
    Input("reloadData", "n_clicks"),
    State("graph", "figure"),
    prevent_initial_call=True,
)
def on_interact(toggle_n, dropdown_val, showall_n, clearall_n, reload_n, current_fig):
    """Handle all UI interactions including data reload."""
    triggered_id = ctx.triggered_id
    status_msg = ""

    # --- Reload Data ---
    if triggered_id == "reloadData":
        # 1. Snapshot current trace visibility from the old figure
        old_vis = {}
        if current_fig and 'data' in current_fig:
            for trace in current_fig['data']:
                name = trace.get('name', '')
                if name:
                    weapon_name = name.split(" (ID:")[0]
                    old_vis[weapon_name] = trace.get('visible', True)

        # 2. Reload data from disk
        wd.reload_data()

        # 3. Build fresh figure (base: all hidden)
        new_fig = wd.getMasterFigure(hide=True)

        # 4. Restore previous visibility for weapons that still exist
        for trace in new_fig.data:
            weapon_name = trace.name.split(" (ID:")[0]
            if weapon_name in old_vis:
                trace.visible = old_vis[weapon_name]

        new_options = [{"label": w.name, "value": w.name} for w in wd.weapons]
        new_val = dropdown_val if dropdown_val and any(w.name == dropdown_val for w in wd.weapons) else None
        status_msg = "Data reloaded"
        return new_fig, new_options, new_val, status_msg

    # --- Build figure from current state ---
    updated_figure = go.Figure(current_fig)

    if triggered_id == "toggleVisibility" and dropdown_val is not None:
        weapon = wd.getWeaponByName(dropdown_val)
        if weapon is not None:
            title = wd.getTitleByWeapon(weapon)
            for i in range(len(updated_figure.data)):
                if updated_figure.data[i].name == title:
                    updated_figure.data[i].visible = not updated_figure.data[i].visible
                    break
        wd.updateLayout(updated_figure)
        return updated_figure, no_update, no_update, status_msg

    elif triggered_id == "showAll":
        return wd.getMasterFigure(hide=False), no_update, no_update, status_msg

    elif triggered_id == "clearAll":
        return wd.getMasterFigure(hide=True), no_update, no_update, status_msg

    # Dropdown selection alone should also update the figure
    wd.updateLayout(updated_figure)
    return updated_figure, no_update, no_update, status_msg


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def run_dash(host="127.0.0.1", port=8050, debug=False):
    """Start the Dash server."""
    app.run(host=host, port=port, debug=debug)


def run_browser(host="127.0.0.1", port=8050):
    """Run in browser only (no native window)."""
    print(f" * Starting server at http://{host}:{port}")
    run_dash(host=host, port=port)


def run_window(host="127.0.0.1", port=8050):
    """Run with a native desktop window via pywebview."""
    try:
        import webview
    except ImportError:
        print("pywebview is not installed. Falling back to browser mode.")
        print("Install with: pip install pywebview")
        run_browser(host=host, port=port)
        return

    import threading

    # Use a module-level flag so the thread doesn't hold up startup
    server_ready = threading.Event()

    def start_server():
        run_dash(host=host, port=port)
        server_ready.set()

    # Start Dash in background
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Wait for the server to be ready
    for _ in range(100):
        try:
            import urllib.request
            urllib.request.urlopen(f"http://{host}:{port}/")
            break
        except Exception:
            time.sleep(0.1)

    server_ready.set()
    webview.create_window(
        "Shooter Game Stat Analyser",
        f"http://{host}:{port}/",
        width=int(wd.generalSettings.get("sizeX", 1200)) + 80,
        height=int(wd.generalSettings.get("sizeY", 600)) + 160,
        resizable=True,
    )
    webview.start()


if __name__ == "__main__":
    if "--browser" in sys.argv:
        run_browser()
    else:
        run_window()
