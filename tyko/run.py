from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from .exceptions import DataError
from .data_provider import DataProvider
from .routes import Routes


def create_app(app=None):
    if app is None:
        app = Flask(__name__)

    app.config.from_object("tyko.config.Config")
    app.config.from_envvar("TYKO_SETTINGS", True)

    app.register_error_handler(DataError, handle_error)

    database = SQLAlchemy(app)
    data_provider = DataProvider(database.engine)
    app_routes = Routes(data_provider, app)
    # if init_db:
    #     init_database(data_provider.db_engine)

    app_routes.init_api_routes()
    app_routes.init_website_routes()
    return app


def main() -> None:
    """Run as a local program and not for production"""

    my_app = create_app()
    my_app.run()


def handle_error(error):
    return make_response(error.message, error.status_code)
