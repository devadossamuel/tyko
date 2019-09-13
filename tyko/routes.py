# pylint: disable=invalid-name, not-an-iterable

from dataclasses import dataclass, field
from typing import Any, List
from flask import Flask, jsonify, render_template
import tyko
from tyko.data_provider import DataProvider

the_app = Flask(__name__)


@dataclass
class Route:
    rule: str
    method: str
    viewFunction: Any
    methods: List[str] = field(default_factory=lambda: ["GET"])


@dataclass
class APIEntity:
    entity_type: str
    rules: List[Route] = field(default_factory=list)


@dataclass
class EntityPage:
    entity_type: str
    entity_list_page: str
    rules: List[Route] = field(default_factory=list)


all_entities = set()
all_forms = set()


class Routes:

    def __init__(self, db_engine: DataProvider, app) -> None:
        self.db_engine = db_engine
        self.app = app
        self.mw = tyko.Middleware(self.db_engine)
        self.wr = WebsiteRoutes(self.mw)

    def init_api_routes(self) -> None:
        project = \
            tyko.ENTITIES["project"].factory(self.db_engine).middleware()

        collection = \
            tyko.ENTITIES["collection"].factory(self.db_engine).middleware()

        item = \
            tyko.ENTITIES["item"].factory(self.db_engine).middleware()

        project_object = \
            tyko.ENTITIES["object"].factory(self.db_engine).middleware()

        if self.app:
            entities = [
                APIEntity("Projects", rules=[
                    Route("/api/project", "projects",
                          lambda serialize=True: project.get(serialize)),
                    Route("/api/project/<string:id>", "project_by_id",
                          lambda id: project.get(id=id)),
                    Route("/api/project/", "add_project",
                          project.create,
                          methods=["POST"]),
                    Route("/api/project/<string:id>", "update_project",
                          lambda id: project.update(id=id),
                          methods=["PUT"]),
                    Route("/api/project/<string:id>", "delete_project",
                          lambda id: project.delete(id=id),
                          methods=["DELETE"]),
                    ]),
                APIEntity("Collection", rules=[
                    Route("/api/collection", "collection",
                          lambda serialize=True: collection.get(serialize)),
                    Route("/api/collection/<string:id>", "collection_by_id",
                          lambda id: collection.get(id=id)),
                    Route("/api/collection/", "add_collection",
                          collection.create,
                          methods=["POST"])
                    ]),
                APIEntity("Formats", rules=[
                    Route("/api/format", "formats",
                          self.mw.get_formats
                          )
                    ]),
                APIEntity("Item", rules=[
                    Route("/api/item", "item",
                          lambda serialize=True: item.get(serialize),
                          methods=["GET"]),
                    Route("/api/item/<string:id>", "item_by_id",
                          lambda id: item.get(id=id),
                          methods=["GET"]),
                    Route("/api/item/", "add_item",
                          item.create,
                          methods=["POST"])

                    ]),
                APIEntity("Object", rules=[
                    Route("/api/object", "object",
                          lambda serialize=True: project_object.get(serialize),
                          methods=["GET"]
                          ),
                    Route("/api/object/<string:id>", "object_by_id",
                          lambda id: project_object.get(id=id)),
                    Route("/api/object/", "add_object",
                          project_object.create,
                          methods=["POST"])
                    ])

            ]

            for entity in entities:
                for rule in entity.rules:
                    self.app.add_url_rule(rule.rule, rule.method,
                                          rule.viewFunction,
                                          methods=rule.methods)

            # ##############
            self.app.add_url_rule(
                "/api",
                "list_routes",
                list_routes,
                methods=["get"],
                defaults={"app": self.app}
            )

    def init_website_routes(self):

        static_web_routes = [
            Route("/", "page_index", self.wr.page_index),
            Route("/about", "page_about", self.wr.page_about),
            ]

        simple_pages = []
        for entity in ["project",
                       "item",
                       "object",
                       "collection"
                       ]:

            simple_pages.append(
                tyko.ENTITIES[entity].factory(self.db_engine).web_frontend()
            )

        entity_pages = [
            EntityPage(
                "Formats",
                "page_formats",
                rules=[
                    Route(
                        "/format",
                        "page_formats",
                        self.wr.page_formats),
                ]),
        ]

        for simple_page in simple_pages:
            entity_pages.append(
                EntityPage(
                    simple_page.entity_title,
                    simple_page.entity_list_page_name,
                    rules=[
                        Route(
                            simple_page.entity_rule,
                            simple_page.entity_list_page_name,
                            simple_page.list
                        )
                    ]
                )
            )

        if self.app:
            for rule in static_web_routes:
                self.app.add_url_rule(rule.rule, rule.method,
                                      rule.viewFunction)

            for entity in entity_pages:
                for rule in entity.rules:
                    all_entities.add((entity.entity_type,
                                      entity.entity_list_page))

                    self.app.add_url_rule(rule.rule, rule.method,
                                          rule.viewFunction)
            for form_page in tyko.frontend.all_forms:
                all_forms.add((form_page.form_title, form_page.form_page_name))
                self.app.add_url_rule(form_page.form_page_rule,
                                      form_page.form_page_name,
                                      form_page.create)


class Routers:
    def __init__(self, middleware: tyko.Middleware) -> None:
        self.middleware = middleware


class WebsiteRoutes(Routers):

    @staticmethod
    def page_index():
        return render_template("index.html", selected_menu_item="index",
                               entities=all_entities,
                               all_forms=all_forms
                               )

    @staticmethod
    def page_about():
        return render_template("about.html", selected_menu_item="about",
                               entities=all_entities,
                               all_forms=all_forms
                               )

    def page_formats(self):

        formats = self.middleware.get_formats(serialize=False)
        return render_template(
            "formats.html",
            selected_menu_item="formats",
            formats=formats,
            entities=all_entities,
            all_forms=all_forms
        )


def list_routes(app):
    results = []
    for rt in app.url_map.iter_rules():
        results.append({
            "methods": list(rt.methods),
            "route": str(rt)
        })
    return jsonify(results)
