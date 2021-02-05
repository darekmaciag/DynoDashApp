import os

from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import psycopg2
from psycopg2.extras import RealDictCursor

# Local imports
from app.database import get_conn


def get_navbar():
    """Get a Bootstrap 4 navigation bar for our single-page application's HTML layout"""

    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Blog", href="https://mccarthysean.dev")),
            dbc.NavItem(dbc.NavLink("IJACK", href="https://myijack.com")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("References", header=True),
                    dbc.DropdownMenuItem("Dash", href="https://dash.plotly.com/"),
                    dbc.DropdownMenuItem("Dash Bootstrap Components", href="https://dash-bootstrap-components.opensource.faculty.ai/"),
                    dbc.DropdownMenuItem("Testdriven", href="https://testdriven.io/"),
                ],
                nav=True,
                in_navbar=True,
                label="Links",
            ),
        ],
        brand="Home",
        brand_href="/",
        color="dark",
        dark=True,
    )


def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return dbc.Container(
        [
            # Just the navigation bar at the top for now...
            # Stay tuned for part 3!
            get_navbar(),
        ], 
    )