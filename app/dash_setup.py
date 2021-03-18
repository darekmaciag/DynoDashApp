import dash
from flask.helpers import get_root_path
import dash_auth
import os
import dash_bootstrap_components as dbc

def register_dashapps(app):
    """
    Register Dash apps with the Flask app
    """
    VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'password'
    }

    external_stylesheets = [dbc.themes.SKETCHY]
    
    # external JavaScript files
    external_scripts = [
        "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js",
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js",
    ]

    meta_viewport = [{
        "name": "viewport", 
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
    }]

    dashapp = dash.Dash(
        __name__,
        server = app,
        url_base_pathname = '/',
        assets_folder = get_root_path(__name__) + '/static_dash/', 
        meta_tags = meta_viewport, 
        external_scripts = external_scripts,
        external_stylesheets = external_stylesheets,
        suppress_callback_exceptions=True
    )

    dashapp.enable_dev_tools(
    dev_tools_ui=False,
    dev_tools_serve_dev_bundles=False,
    dev_tools_hot_reload=False,
    )

    dashapp.title = 'DynoDashApp'
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
    import redis
    with app.app_context():
        dashapp.layout = get_layout
        
        register_callbacks(dashapp)

    return None