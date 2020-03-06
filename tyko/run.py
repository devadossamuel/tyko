import sys

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy

from .database import init_database
from .exceptions import DataError
from .data_provider import DataProvider
from .routes import Routes


def create_app(app=None):
    if app is None:
        app = Flask(__name__)

    app.config.from_object("tyko.config.Config")
    app.config.from_envvar("TYKO_SETTINGS", True)

    app.register_error_handler(DataError, handle_error)

    database = SQLAlchemy(app, engine_options={"pool_pre_ping": True})
    engine = database.get_engine()
    data_provider = DataProvider(engine)
    app_routes = Routes(data_provider, app)

    app_routes.init_api_routes()
    app_routes.init_website_routes()
    return app


def main() -> None:

    if "init-db" in sys.argv:
        my_app = Flask(__name__)
        my_app.config.from_object("tyko.config.Config")
        my_app.config.from_envvar("TYKO_SETTINGS", True)
        database = SQLAlchemy(my_app)
        data_provider = DataProvider(database.engine)
        print("Initializing Database")
        init_database(data_provider.db_engine)
        print("Database initialized")
        sys.exit(0)
    my_app = create_app()
    # Run as a local program and not for production
    my_app.run()


def handle_error(error):
    return make_response(error.message, error.status_code)
