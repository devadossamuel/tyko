import sys

from flask import Flask
from avforms import routes, database
from avforms.config import setup_cli_parser
from avforms.data_provider import DataProvider


def create_app(db_engine_source: str, app=None, init_db=False):
    if app is None:
        app = Flask(__name__)
    data_provider = DataProvider(db_engine_source)
    app_routes = routes.Routes(data_provider, app)
    if init_db:
        database.init_database(data_provider.db_engine)

    app_routes.init_api_routes()
    app_routes.init_website_routes()
    return app


def main() -> None:
    """Run as a local program and not for production"""

    parser = setup_cli_parser()
    args = parser.parse_args()

    # Validate that the database can be connected to
    print(args)
    my_app = create_app(args.db_engine)
    my_app.run()
