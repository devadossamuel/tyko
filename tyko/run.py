import sys
import logging

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from .database import init_database
from .exceptions import DataError
from .data_provider import DataProvider, get_schema_version
from .scheme import ALEMBIC_VERSION
from .routes import Routes


def is_correct_db_version(app, database) -> bool:
    try:
        version = get_schema_version(db_engine=database.get_engine())
        if version is None:
            app.logger.error("No version information found")
            return False
    except OperationalError as exc:
        app.logger.error(
            "Problem getting version information. Reason given: {}".format(exc))
        return False
    return version == ALEMBIC_VERSION


def create_app(app=None, verify_db=True) -> Flask:
    if app is None:
        app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Loading configurations")
    app.config.from_object("tyko.config.Config")
    app.config.from_envvar("TYKO_SETTINGS", True)

    app.register_error_handler(DataError, handle_error)

    app.logger.info("Configuring database")
    database = SQLAlchemy(app, engine_options={"pool_pre_ping": True})
    engine = database.get_engine()

    app.logger.info("Loading database connection")
    data_provider = DataProvider(engine)

    app.logger.info("Checking database schema version")
    if verify_db is True and not is_correct_db_version(app, database):
        app.logger.critical(f"Database requires alembic version "
                            f"{ALEMBIC_VERSION}. Please migrate or initialize "
                            f"database and try again.")
        app.add_url_rule("/", "unable_to_load", page_failed_on_startup)
        return app

    app_routes = Routes(data_provider, app)
    app.logger.info("Initializing API routes")
    app_routes.init_api_routes()
    app.logger.info("Initializing Website routes")
    app_routes.init_website_routes()

    return app


def page_failed_on_startup():
    return make_response("Tyko failed during started", 503)


def main() -> None:

    if "init-db" in sys.argv:
        my_app = Flask(__name__)
        my_app.config.from_object("tyko.config.Config")
        my_app.config.from_envvar("TYKO_SETTINGS", True)
        database = SQLAlchemy(my_app)
        data_provider = DataProvider(database.engine)
        my_app.logger.info("Initializing Database")  # pylint: disable=E1101
        init_database(data_provider.db_engine)
        sys.exit(0)
    my_app = create_app()
    if my_app is not None:
        # Run as a local program and not for production
        my_app.run()


def handle_error(error):
    return make_response(error.message, error.status_code)
