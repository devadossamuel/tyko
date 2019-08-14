import sys

from flask import Flask
from avforms import routes
from avforms.config import setup_cli_parser


def create_app(db_engine, app=None):
    if app is None:
        app = Flask(__name__)
    app_routes = routes.Routes(db_engine, app)
    if not app_routes.is_valid():
        sys.exit(1)

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
