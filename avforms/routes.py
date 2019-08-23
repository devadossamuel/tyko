from flask import Flask, jsonify, render_template
import avforms
from avforms.data_provider import DataProvider

the_app = Flask(__name__)


class Routes:

    def __init__(self, db_engine: DataProvider, app) -> None:
        self.db_engine = db_engine
        self.app = app
        mw = avforms.Middleware(self.db_engine)
        self.wr = WebsiteRoutes(mw)
        self.ar = APIRoutes(mw)

    def init_api_routes(self) -> None:

        if self.app:
            # ###### projects
            self.app.add_url_rule(
                "/api/project",
                "projects",
                self.ar.get_projects
            )

            self.app.add_url_rule(
                "/api/project/<string:id>",
                "project_by_id",
                self.ar.get_project_by_id,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/project/",
                "add_project",
                self.ar.add_project,
                methods=["POST"]
            )

            self.app.add_url_rule(
                "/api/project/<string:id>",
                "update_project",
                self.ar.update_project,
                methods=["PUT"]
            )
            self.app.add_url_rule(
                "/api/project/<string:id>",
                "delete_project",
                self.ar.delete_project,
                methods=["DELETE"]
            )

            # ###### collections
            self.app.add_url_rule(
                "/api/collection/<string:id>",
                "collection_by_id",
                self.ar.collection_by_id,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/collection",
                "collection",
                self.ar.get_collections,
                methods=["GET"]
            )

            self.app.add_url_rule(
                "/api/collection/",
                "add_collection",
                self.ar.add_collection,
                methods=["POST"]
            )

            # ###### Formats
            self.app.add_url_rule(
                "/api/format",
                "formats",
                self.ar.get_formats
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

        if self.app:
            self.app.add_url_rule(
                "/",
                "page_index",
                self.wr.page_index
            )

            self.app.add_url_rule(
                "/about",
                "page_about",
                self.wr.page_about
            )

            self.app.add_url_rule(
                "/collection",
                "page_collections",
                self.wr.page_collections
            )

            self.app.add_url_rule(
                "/project",
                "page_projects",
                self.wr.page_projects
            )

            self.app.add_url_rule(
                "/format",
                "page_formats",
                self.wr.page_formats
            )


class Routers:
    def __init__(self, middleware: avforms.Middleware) -> None:
        self.middleware = middleware


class APIRoutes(Routers):

    def get_projects(self, serialize=True):
        return self.middleware.get_projects(serialize)

    def get_project_by_id(self, id):
        return self.middleware.get_project_by_id(id)

    def get_collections(self, serialize=True):
        return self.middleware.get_collections(serialize)

    def collection_by_id(self, id):
        return self.middleware.collection_by_id(id)

    def get_formats(self, serialize=True):
        return self.middleware.get_formats(serialize)

    def add_project(self):
        return self.middleware.add_project()

    def update_project(self, id):
        return self.middleware.update_project(id)

    def delete_project(self, id):
        return self.middleware.delete_project(id)

    def add_collection(self):
        return self.middleware.add_collection()


class WebsiteRoutes(Routers):

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
