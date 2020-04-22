# pylint: disable=invalid-name, not-an-iterable

from dataclasses import dataclass, field
from typing import Any, List, Iterator, Tuple, Callable
from flask import jsonify, render_template, views

import tyko.views.files
from . import middleware
from .data_provider import DataProvider
from . import frontend
from .views.object_item import ObjectItemNotesAPI, ObjectItemAPI
from .views.object_item import ItemAPI
from .views.project import ProjectNotesAPI, ProjectAPI
from .views.project_object import ProjectObjectAPI, ObjectApi, \
    ProjectObjectNotesAPI


@dataclass
class Route:
    rule: str
    method: str
    view_function: Any
    methods: List[str] = field(default_factory=lambda: ["GET"])


@dataclass
class APIEntity:
    entity_type: str
    rules: List[Route] = field(default_factory=list)


@dataclass
class EntityPage:
    entity_type: str
    entity_list_page: str
    routes: List[Route] = field(default_factory=list)


_all_entities = set()


class NotesAPI(views.MethodView):
    def __init__(self,
                 notes_middleware: middleware.NotestMiddlwareEntity) -> None:
        self._middleware = notes_middleware

    def delete(self, note_id: int):
        return self._middleware.delete(id=note_id)

    def get(self, note_id: int):
        return self._middleware.get(id=note_id)

    def put(self, note_id: int):
        return self._middleware.update(id=note_id)


class CollectionsAPI(views.MethodView):
    def __init__(self,
                 collection: middleware.CollectionMiddlwareEntity) -> None:

        self._collection = collection

    def get(self, collection_id: int):
        return self._collection.get(id=collection_id)

    def put(self, collection_id: int):
        return self._collection.update(id=collection_id)

    def delete(self, collection_id: int):
        return self._collection.delete(id=collection_id)


class Routes:

    def __init__(self, db_engine: DataProvider, app) -> None:
        self.db_engine = db_engine
        self.app = app
        self.mw = middleware.Middleware(self.db_engine)

    def init_api_routes(self) -> None:

        if self.app:
            project = middleware.ProjectMiddlwareEntity(self.db_engine)
            collection = middleware.CollectionMiddlwareEntity(self.db_engine)
            item = middleware.ItemMiddlwareEntity(self.db_engine)
            notes = middleware.NotestMiddlwareEntity(self.db_engine)

            project_object = middleware.ObjectMiddlwareEntity(self.db_engine)
            api_entities = [
                APIEntity("Projects", rules=[
                    Route("/api/project", "projects",
                          lambda serialize=True: project.get(serialize)),
                    Route("/api/project/", "add_project",
                          project.create,
                          methods=["POST"]),
                    ]),
                APIEntity("Collection", rules=[
                    Route("/api/collection", "collections",
                          lambda serialize=True: collection.get(serialize)),
                    Route("/api/collection/", "add_collection",
                          collection.create,
                          methods=["POST"]),
                    ]),
                APIEntity("Formats", rules=[
                    Route("/api/format", "formats",
                          self.mw.get_formats
                          ),
                    Route("/api/format/<string:id>", "format_by_id",
                          self.mw.get_formats_by_id
                          ),
                    ]),
                APIEntity("Item", rules=[
                    Route("/api/item", "items",
                          lambda serialize=True: item.get(serialize),
                          methods=["GET"]),
                    Route("/api/item/", "add_item",
                          item.create,
                          methods=["POST"]),
                    ]),
                APIEntity("Object", rules=[
                    Route("/api/object", "objects",
                          lambda serialize=True: project_object.get(serialize),
                          methods=["GET"]
                          ),
                    Route("/api/object/<int:id>-pbcore.xml",
                          "object_pbcore",
                          lambda id: project_object.pbcore(id=id)
                          ),
                    Route("/api/object/", "add_object",
                          project_object.create,
                          methods=["POST"]),
                    ]),
                APIEntity("Notes", rules=[
                    Route("/api/notes", "notes",
                          lambda serialize=True: notes.get(serialize),
                          methods=["GET"]),
                    Route("/api/notes/", "add_note",
                          notes.create,
                          methods=["POST"]),
                    ])

            ]

            for entity in api_entities:
                for rule in entity.rules:
                    self.app.add_url_rule(rule.rule, rule.method,
                                          rule.view_function,
                                          methods=rule.methods)

            self.app.add_url_rule(
                "/api/project/<string:project_id>/notes",
                "project_add_note",
                project.add_note,
                methods=["POST"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>",
                "project",
                view_func=ProjectAPI.as_view("projects", project=project),
                methods=["GET", "PUT", "DELETE"]
            )

            self.app.add_url_rule(
                "/api/object/<int:object_id>",
                view_func=ObjectApi.as_view("object",
                                            object_middleware=project_object),
                methods=[
                    "GET",
                    "DELETE",
                    "PUT"
                ]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object",
                "project_add_object",
                project.add_object,
                methods=["POST"]
            )

            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>",
                "project_object",
                view_func=ProjectObjectAPI.as_view("project_objects",
                                                   project=project),
                methods=["DELETE"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item",
                "project_object_add_item",
                lambda project_id, object_id: project_object.add_item(
                    project_id=project_id, object_id=object_id),
                methods=["POST"],
            )

            self.app.add_url_rule(
                "/api/project/<int:project_id>/notes/<int:note_id>",
                view_func=ProjectNotesAPI.as_view("project_notes",
                                                  project=project),
                methods=["PUT", "DELETE"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/notes",
                "project_object_add_note",
                project_object.add_note,
                methods=["POST"]
            )

            self.app.add_url_rule(
                "/api/collection/<int:collection_id>",
                view_func=CollectionsAPI.as_view(
                    "collection",
                    collection=collection),
                methods=[
                    "GET",
                    "PUT",
                    "DELETE"
                ]
            )
            self.app.add_url_rule(
                "/api/note/<int:note_id>",
                view_func=NotesAPI.as_view(
                    "note",
                    notes_middleware=notes),
                methods=[
                    "GET",
                    "PUT",
                    "DELETE"
                ]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/notes/<int:note_id>",  # noqa: E501 pylint: disable=C0301
                view_func=ProjectObjectNotesAPI.as_view(
                    "object_notes",
                    project_object=project_object),
                methods=["PUT", "DELETE"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/notes",  # noqa: E501 pylint: disable=C0301
                "project_object_item_add_note",
                lambda project_id, object_id, item_id: item.add_note(item_id),
                methods=["POST"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/file",  # noqa: E501 pylint: disable=C0301
                "project_object_item_add_file",
                item.add_file,
                methods=["POST"]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/notes/<int:note_id>",  # noqa: E501 pylint: disable=C0301
                view_func=ObjectItemNotesAPI.as_view(
                    "item_notes",
                    item=item),
                methods=["PUT", "DELETE"]
            )

            self.app.add_url_rule(
                "/api/item/<int:item_id>",
                view_func=ItemAPI.as_view(
                    "item",
                    provider=self.db_engine),
                methods=[
                    "GET",
                    "PUT",
                    "DELETE"
                ]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>",  # noqa: E501 pylint: disable=C0301
                view_func=ObjectItemAPI.as_view(
                    "object_item",
                    parent=project_object),
                methods=[
                    "DELETE"
                ]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/files",  # noqa: E501 pylint: disable=C0301
                view_func=tyko.views.files.ItemFilesAPI.as_view(
                    "item_files",
                    provider=self.db_engine
                ),
                methods=[
                    "POST",
                    "GET"
                ]
            )
            self.app.add_url_rule(
                "/api/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/files/<int:file_id>",  # noqa: E501 pylint: disable=C0301
                view_func=tyko.views.files.FileAPI.as_view(
                    "item_file_details",
                    provider=self.db_engine
                ),
                methods=[
                    "GET",
                    "PUT",
                    "DELETE"
                ]

            )
            self.app.add_url_rule(
                "/api/file/<int:file_id>/note",
                view_func=tyko.views.files.FileNotesAPI.as_view(
                    "file_notes",
                    provider=self.db_engine
                ),
                methods=[
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"
                ]
            )
            self.app.add_url_rule(
                "/api/file/<int:file_id>/annotations",
                view_func=tyko.views.files.FileAnnotationsAPI.as_view(
                    "file_annotations",
                    provider=self.db_engine
                ),
                methods=[
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE"

                ]
            )

            self.app.add_url_rule(
                "/api/file/annotation_types",
                view_func=tyko.views.files.FileAnnotationTypesAPI.as_view(
                    "file_annotation_types",
                    provider=self.db_engine
                ),
                methods=[
                    "GET",
                    "POST",
                    "DELETE"
                ]
            )

            # TODO: add url rule for editing file annotation types

            self.app.add_url_rule(
                "/api",
                "list_routes",
                list_routes,
                methods=["get"],
                defaults={"app": self.app}
            )

    def init_website_routes(self):
        about_page = frontend.AboutPage()
        index_page = frontend.IndexPage()
        more_page = frontend.MoreMenuPage()
        new_collection_page = frontend.NewCollectionForm()

        static_web_routes = [
            Route("/", "page_index", index_page.render_page),
            Route("/about", "page_about", about_page.render_page),
            Route("/more", "page_more", more_page.render_page),
            Route("/collection/new", "form_new_collection",
                  new_collection_page.render_page),
            ]

        simple_pages = []

        entity_pages = [
            EntityPage(
                "Formats",
                "page_formats",
                routes=[
                    Route(
                        "/format",
                        "page_formats",
                        lambda: page_formats(self.mw)
                    ),
                ]),

            EntityPage(
                "Objects",
                "page_object",
                routes=[
                    Route(
                        "/object",
                        "page_object",
                        lambda: frontend.ObjectFrontend(
                            self.mw.data_provider).list()
                    ),
                    Route(
                        "/object/<int:object_id>",
                        "page_object_details",
                        lambda object_id: frontend.ObjectFrontend(
                            self.mw.data_provider).display_details(
                                object_id, show_bread_crumb=False)
                    ),
                ]),
            EntityPage(
                "Items",
                "page_item",
                routes=[
                    Route(
                        "/item",
                        "page_item",
                        lambda: frontend.ItemFrontend(
                            self.mw.data_provider).list()
                    ),
                    Route(
                        "/item/<string:item_id>",
                        "page_item_details",
                        lambda item_id: frontend.ItemFrontend(
                            self.mw.data_provider).display_details(
                                item_id, show_bread_crumb=False)
                    ),
                ]),
            EntityPage(
                "Collections",
                "page_collections",
                routes=[
                    Route(
                        "/collection",
                        "page_collections",
                        lambda: frontend.CollectiontFrontend(
                            self.mw.data_provider).list()
                    ),
                    Route(
                        "/collection/<string:collection_id>",
                        "page_collection_details",
                        lambda collection_id: frontend.CollectiontFrontend(
                            self.mw.data_provider).display_details(
                                collection_id)
                    ),
                ]),
        ]
        for simple_page in simple_pages:
            entity_pages.append(
                EntityPage(
                    simple_page.entity_title,
                    simple_page.entity_list_page_name,
                    routes=[
                        Route(
                            rule=simple_page.entity_rule,
                            method=simple_page.entity_list_page_name,
                            view_function=simple_page.list,
                        )
                    ]
                )
            )
        project_page = EntityPage(
            "Projects",
            "page_project",
            routes=[
                Route(
                    "/project",
                    "page_projects",
                    frontend.ProjectFrontend(self.mw.data_provider).list
                ),
                Route(
                    "/project/<int:project_id>",
                    "page_project_details",
                    lambda project_id: frontend.ProjectFrontend(
                        self.mw.data_provider).display_details(
                            project_id,
                            show_bread_crumb=True)
                ),
                Route(
                    "/project/<int:project_id>/object/<int:object_id>",
                    "page_project_object_details",
                    lambda project_id, object_id: frontend.ObjectFrontend(
                        self.mw.data_provider).display_details(
                            object_id, show_bread_crumb=True)
                ),
                Route(
                    "/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>",  # noqa: E501 pylint: disable=C0301
                    "page_project_object_item_details",
                    lambda project_id, object_id, item_id:
                    frontend.ItemFrontend(
                        self.mw.data_provider).display_details(
                            item_id,
                            project_id=project_id,
                            object_id=object_id,
                            show_bread_crumb=True)
                ),
                Route(
                    "/project/create/",
                    "page_project_new",
                    frontend.ProjectFrontend(self.mw.data_provider).create
                )
            ]
        )

        if self.app:
            # TODO: Make frontend route generator into a generator function
            for rule in static_web_routes:
                self.app.add_url_rule(rule.rule, rule.method,
                                      rule.view_function)
            for rule in project_page.routes:
                self.app.add_url_rule(rule.rule,
                                      rule.method,
                                      rule.view_function)

            for entity in entity_pages:
                for rule in entity.routes:
                    _all_entities.add((entity.entity_type,
                                       entity.entity_list_page))

                    self.app.add_url_rule(rule.rule, rule.method,
                                          rule.view_function)

            for route, route_name, func in get_frontend_page_routes(
                    self.mw.data_provider):

                self.app.add_url_rule(route, route_name, func)


def get_frontend_page_routes(data_prov) -> Iterator[Tuple[str, str, Callable]]:
    # TODO: add frontend routes to here

    file_details = frontend.FileDetailsFrontend(data_prov)
    yield (
        "/project/<int:project_id>/object/<int:object_id>/item/<int:item_id>/files/<int:file_id>",  # noqa: E501 pylint: disable=C0301
        "page_file_details",
        file_details.display_details)


def page_formats(middleware_source):
    formats = middleware_source.get_formats(serialize=False)
    return render_template(
        "formats.html",
        selected_menu_item="formats",
        formats=formats,
        entities=_all_entities
    )


def list_routes(app):
    results = []
    for rt in app.url_map.iter_rules():
        results.append({
            "endpoint": rt.endpoint,
            "methods": list(rt.methods),
            "route": str(rt)
        })
    return jsonify(results)
