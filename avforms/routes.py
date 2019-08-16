import sys

import sqlalchemy.exc
from flask import Flask, jsonify, render_template
from avforms import middleware

the_app = Flask(__name__)


class Routes:

    def __init__(self, db_engine, app) -> None:
        self.db_engine = db_engine
        self.app = app

    def is_valid(self):
        try:
            middleware.DataProvider(self.db_engine)
        except sqlalchemy.exc.OperationalError as e:
            print(e, file=sys.stderr)
            return False
        return True

    def init_api_routes(self):
        mw = middleware.Middleware("sqlite:///dummy.db?check_same_thread=False")
        ar = APIRoutes(self.db_engine)
        # TODO: refactor this into a API Routes class
        # mw = middleware.Middleware("sqlite:///dummy.db?check_same_thread=False")
        if self.app:
            # ###### projects
            self.app.add_url_rule(
                "/api/project",
                "projects",
                ar.get_projects
            )

            self.app.add_url_rule(
                "/api/project/<string:id>",
                "project_by_id",
                mw.get_project_by_id,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/project/",
                "add_project",
                mw.add_project,
                methods=["POST"]
            )

            self.app.add_url_rule(
                "/api/project/<string:id>",
                "update_project",
                mw.update_project,
                methods=["PUT"]
            )
            self.app.add_url_rule(
                "/api/project/<string:id>",
                "delete_project",
                mw.delete_project,
                methods=["DELETE"]
            )

            # ###### collections
            self.app.add_url_rule(
                "/api/collection/<string:id>",
                "collection_by_id",
                mw.collection_by_id,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/collection",
                "collection",
                ar.get_collections,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/collection/",
                "add_collection",
                mw.add_collection,
                methods=["POST"]
            )

            # ###### Formats
            self.app.add_url_rule(
                "/api/format",
                "formats",
                mw.get_formats
            )

            # ##############
            self.app.add_url_rule(
                "/api",
                "list_routes",
                list_routes,
                methods=["get"],
                defaults={"app": self.app}
            )

    def init_website_routes(self):
        wr = WebsiteRoutes(self.db_engine)
        if self.app:
            self.app.add_url_rule(
                "/",
                "page_index",
                wr.page_index
            )

            self.app.add_url_rule(
                "/about",
                "page_about",
                wr.page_about
            )

            self.app.add_url_rule(
                "/collection",
                "page_collections",
                wr.page_collections
            )

            self.app.add_url_rule(
                "/project",
                "page_projects",
                wr.page_projects
            )

            self.app.add_url_rule(
                "/format`",
                "page_formats",
                wr.page_formats
            )

class APIRoutes:
    def __init__(self, db_engine) -> None:
        self.db_engine = db_engine
        self.middleware = middleware.Middleware(self.db_engine)


    def get_projects(self, serialize=True):

        return self.middleware.get_projects(serialize)

    def get_collections(self, serialize=True):
        return  self.middleware.get_collections(serialize)


class WebsiteRoutes:
    def __init__(self, db_engine) -> None:
        self.db_engine = db_engine
        self.middleware = middleware.Middleware(self.db_engine)

    @staticmethod
    def page_index():
        return render_template("index.html", selected_menu_item="index")

    @staticmethod
    def page_about():
        return render_template("about.html", selected_menu_item="about")

    def page_collections(self):
        collections = self.middleware.get_collections(serialize=False)
        return render_template(
            "collections.html",
            selected_menu_item="collection",
            collections=collections
        )

    def page_projects(self):
        projects = self.middleware.get_projects(serialize=False)
        return render_template(
            "projects.html",
            selected_menu_item="projects",
            projects=projects
        )

    def page_formats(self):
        formats = self.middleware.get_formats(serialize=False)
        return render_template(
            "formats.html",
            selected_menu_item="formats",
            formats=formats
        )



def list_routes(app):
    results = []
    for rt in app.url_map.iter_rules():
        results.append({
            "methods": list(rt.methods),
            "route": str(rt)
        })
    return jsonify(results)
