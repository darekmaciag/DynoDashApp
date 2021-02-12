import dash
from flask.helpers import get_root_path
import dash_auth
import os

def register_dashapps(app):
    """
    Register Dash apps with the Flask app
    """
    VALID_USERNAME_PASSWORD_PAIRS = {
    'hello': 'world'
    }

    # external CSS stylesheets
    external_stylesheets = [
        'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/yeti/bootstrap.min.css'
    ]
    
    # external JavaScript files
    external_scripts = [
        "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js",
    ]

    # To ensure proper rendering and touch zooming for all devices, add the responsive viewport meta tag
    meta_viewport = [{
        "name": "viewport", 
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
    }]

    dashapp = dash.Dash(
        __name__,
        # This is where the Flask app gets appointed as the server for the Dash app
        server = app,
        url_base_pathname = '/',
        # Separate assets folder in "static_dash" (optional)
        assets_folder = get_root_path(__name__) + '/static_dash/', 
        meta_tags = meta_viewport, 
        external_scripts = external_scripts,
        external_stylesheets = external_stylesheets,
        suppress_callback_exceptions=True
    )

    dashapp.enable_dev_tools(
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,
    )

    dashapp.title = 'Dash Charts in Single-Page Application'
    auth = dash_auth.BasicAuth(
        dashapp,
        VALID_USERNAME_PASSWORD_PAIRS
    )
    
    
    # Some of these imports should be inside this function so that other Flask
    # stuff gets loaded first, since some of the below imports reference the other
    # Flask stuff, creating circular references
    from app.dashapp.layout import get_layout
    from app.dashapp.callbacks import register_callbacks
    from app.dashapp.motor import task1

    with app.app_context():

        # Assign the get_layout function without calling it yet
        dashapp.layout = get_layout
        
        # Register callbacks
        # Layout must be assigned above, before callbacks
        register_callbacks(dashapp)

    return None