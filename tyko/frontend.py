# pylint: disable=invalid-name

import abc
import collections.abc
from abc import ABC
from typing import Tuple, Set, Optional, Callable, List, Iterator, \
    NamedTuple, Dict
from dataclasses import dataclass

from flask import make_response, render_template, url_for

from . import data_provider


@dataclass
class FormField:
    form_type: str
    form_id: str
    form_user_text: str
    required: bool


@dataclass
class Details:
    name: str
    value: Optional[str] = None
    key: Optional[str] = None
    source_key: Optional[Callable[[], str]] = None
    key_branch: Optional[str] = None
    editable: bool = False


class Breadcrumb(NamedTuple):
    name: str
    link: str
    current: bool


class BreadcrumbBuilder(collections.abc.MutableMapping):
    VALID_CRUMBS = [
        "Project",
        "Object",
        "Item"
    ]

    def __init__(self) -> None:
        self._data: Dict[str, str] = dict()

    def __delitem__(self, v: str) -> None:
        del self._data[v]

    def __getitem__(self, k: str) -> str:
        return self._data[k]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        for k in BreadcrumbBuilder.VALID_CRUMBS:
            if k in self._data:
                yield k, self._data[k]

    def __setitem__(self, k: str, v: str) -> None:
        if k not in BreadcrumbBuilder.VALID_CRUMBS:
            raise ValueError("Not a valid breadcrumb level")
        self._data[k] = v

    def build(self, active_level) -> List[Breadcrumb]:
        if active_level not in BreadcrumbBuilder.VALID_CRUMBS:
            raise ValueError("Not a valid breadcrumb type")

        breadcrumbs: List[Breadcrumb] = list()
        for k in BreadcrumbBuilder.VALID_CRUMBS:
            self._add_crumb(breadcrumbs, k, current=active_level == k)

        return breadcrumbs

    def _add_crumb(self, breadcrumbs: List[Breadcrumb], key, current) -> None:

        if key in self._data:
            breadcrumbs.append(
                Breadcrumb(name=key, link=self._data[key], current=current))


class AbsFrontend(metaclass=abc.ABCMeta):
    @classmethod
    def build_header_context(cls, current_item, context):
        entity_menu = [
            "Collections",
            "Items",
            "Objects",
        ]
        new_context = dict()
        new_context.update(context)
        new_context["selected_menu_item"] = current_item

        for entity_name in entity_menu:
            if current_item == entity_name:
                new_context["is_entity"] = True
                break
        else:
            new_context["is_entity"] = False

        return new_context

    @abc.abstractmethod
    def render_page(self, template, **context):
        """Create a webpage based on the template"""


class IndexPage(AbsFrontend):

    def render_page(self, template="index.html", **context):
        header = self.build_header_context("Home", context=context)
        return render_template(template, **header)


class AboutPage(AbsFrontend):

    def render_page(self, template="about.html", **context):
        header = self.build_header_context("About", context=context)
        return render_template(template, **header)


class MoreMenuPage(AbsFrontend):

    def render_page(self, template="more.html", **context):
        entities: List[Tuple[str, str]] = [
            ("Formats", "page_formats"),
            ("Items", "page_item"),
            ("Objects", "page_object"),
            ("Projects", "page_projects"),
            ("Collections", "page_collections"),
        ]
        forms: List[Tuple[str, str]] = [
            # ("New Collection", "page_new_collection"),
            ("New Item", "page_new_item"),
            ("New Object", "page_new_object"),
            ]
        context['all_forms'] = forms
        header = self.build_header_context("More", context=context)
        header['entities'] = entities
        return render_template(template, **header)


class FrontendEntity(AbsFrontend):
    _entities: Set[Tuple[str, str]] = {
        # ("Formats", "page_formats"),
        ("Items", "page_item"),
        ("Objects", "page_object"),
        ("Collections", "page_collections"),
    }

    def __init__(self, provider: data_provider.DataProvider) -> None:
        self._data_provider = provider

        FrontendEntity._entities.add(
            (self.entity_title, self.entity_list_page_name)
        )

    def display_details(self, entity_id, *args, **kwargs):  # noqa: E501 pylint: disable=unused-argument
        return make_response(
            "{}.display_details not implemented".format(
                self.__class__.__name__), 404)

    def list(self):
        return make_response(
            "{}.list not implemented".format(self.__class__.__name__), 404)

    def render_page(self, template, **context):
        new_context = self.build_header_context(
            current_item=self.entity_title,
            context=context
        )

        return render_template(template, **new_context)

    @property
    @abc.abstractmethod
    def entity_title(self) -> str:
        """Title of the entity as it's meant to be displayed to the user"""

    @property
    @abc.abstractmethod
    def entity_rule(self) -> str:
        """The Rule use to look up webpage that displays the details of the
        entity
        """

    @property
    @abc.abstractmethod
    def entity_list_page_name(self) -> str:
        """The Rule to website that display a list of the given entity"""

    @classmethod
    def all_entities(cls):
        return sorted(cls._entities, key=lambda x: [0])


class FrontendEditable(FrontendEntity):
    @abc.abstractmethod
    def create(self):
        """Generate the page for the create new entity"""

    @abc.abstractmethod
    def edit_details(self, entity_id):
        """Generate the page for the edit an existing entity"""


class ProjectComponentDetailFrontend(FrontendEntity, ABC):  # noqa: E501 pylint: disable=W0223
    @staticmethod
    def build_breadcrumbs(active_level, project_url=None, object_url=None,
                          item_url=None) -> List[Breadcrumb]:

        breadcrumb_builder = BreadcrumbBuilder()

        if project_url is not None:
            breadcrumb_builder['Project'] = project_url

        if object_url is not None:
            breadcrumb_builder['Object'] = object_url

        if item_url is not None:
            breadcrumb_builder['Item'] = item_url

        return breadcrumb_builder.build(active_level)


class ProjectFrontend(ProjectComponentDetailFrontend):

    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ProjectDataConnector(provider.db_session_maker)

    def list(self):
        return self.render_page(template="projects.html",
                                api_path="api/project",
                                )

    @property
    def entity_title(self) -> str:
        return "Projects"

    @property
    def entity_rule(self) -> str:
        return "/project"

    @property
    def entity_list_page_name(self) -> str:
        return "page_projects"

    def display_details(self, entity_id, *args, **kwargs):
        selected_project = self._data_connector.get(
            serialize=True, id=entity_id)

        edit_link = f"{url_for('page_projects')}/{entity_id}/edit"

        fields = [
            Details(name="Title", key="title", editable=True),
            Details(name="Project Code", key="project_code", editable=True),
            Details(name="Status", key="status", editable=True),
            Details(
                name="Current Location",
                key="current_location",
                editable=True
            ),
        ]

        valid_note_types = []
        for note_type in self._data_connector.get_note_types():
            valid_note_types.append((note_type.name, note_type.id))

        return self.render_page(
            template="project_details.html",
            project=selected_project,
            api_path=f"{url_for('.page_index')}api/project/{entity_id}",
            edit_link=edit_link,
            project_id=entity_id,
            valid_note_types=valid_note_types,
            fields=fields,
            breadcrumbs=self.build_breadcrumbs(
                active_level="Project",
                project_url=url_for(
                    "page_project_details",
                    project_id=entity_id
                )
            ),
            show_bread_crumb=True,
            collections=data_provider.CollectionDataConnector(
                self._data_connector.session_maker).get(serialize=True)
            )

    def create(self):
        return self.render_page(template="new_project.html",
                                api_path="/api/project/",
                                title="New Project",
                                on_success_redirect_base="/project/",
                                )

    def render_page(self, template="project_details.html", **context):
        context['itemType'] = "Project"
        return super().render_page(template, **context)


class ItemFrontend(ProjectComponentDetailFrontend):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ItemDataConnector(provider.db_session_maker)

    def list(self):
        return self.render_page(template="items.html",
                                api_path="api/item",
                                row_table="items"
                                )

    def render_page(self, template="items.html", **context):
        context['itemType'] = "Item"
        return super().render_page(template, **context)

    def display_details(self, entity_id, *args, **kwargs):
        selected_item = self._data_connector.get(
            serialize=True, id=entity_id)

        def get_format():
            if selected_item['format'] is not None:
                return selected_item['format']['name'].title()
            return None

        fields = [
            Details(name="Name", key="name", editable=True),
            Details(name="Format", key="format_type", source_key=get_format),
            Details(name="File Name", key="file_name", editable=True),
            Details(name="Medusa UUID", key="medusa_uuid", editable=True),
            Details(name="Object Sequence", key="obj_sequence", editable=True),
        ]

        api_path = f"{url_for('.page_index')}api/item/{entity_id}"
        for f in fields:
            if f.source_key is not None:
                selected_item[f.key] = f.source_key()
        if "show_bread_crumb" in kwargs and kwargs['show_bread_crumb'] is True:
            breadcrumbs = self.build_breadcrumbs(
                active_level="Item",
                project_url=url_for("page_project_details",
                                    project_id=kwargs["project_id"]
                                    ) if "project_id" in kwargs else None,
                item_url="",
                object_url=url_for("page_project_object_details",
                                   project_id=kwargs["project_id"],
                                   object_id=selected_item['parent_object_id'])
            )
        else:
            breadcrumbs = None

        valid_note_types = []
        for note_type in self._data_connector.get_note_types():
            valid_note_types.append((note_type.name, note_type.id))

        return self.render_page(
            template="item_details.html",
            project_id=kwargs.get("project_id"),
            valid_note_types=valid_note_types,
            object_id=selected_item['parent_object_id'],
            fields=fields,
            breadcrumbs=breadcrumbs,
            show_bread_crumb=kwargs.get('show_bread_crumb'),
            api_path=api_path,
            item=selected_item)

    @property
    def entity_title(self) -> str:
        return "Items"

    @property
    def entity_rule(self) -> str:
        return "/item"

    @property
    def entity_list_page_name(self) -> str:
        return "page_item"


class ObjectFrontend(ProjectComponentDetailFrontend):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)
        self._data_provider = provider
        self._data_connector = \
            data_provider.ObjectDataConnector(provider.db_session_maker)

    def list(self):
        return self.render_page(template="objects.html",
                                api_path="api/object",
                                row_table="objects"
                                )

    def create(self):
        return self.render_page(template="object_details.html",
                                api_path="/api/object/",
                                title="New Object",
                                on_success_redirect_base="/object/",
                                )

    @property
    def entity_title(self) -> str:
        return "Objects"

    @property
    def entity_rule(self) -> str:
        return "/object"

    @property
    def entity_list_page_name(self) -> str:
        return "page_object"

    def display_details(self, entity_id, *args, **kwargs):
        fields = [
            Details(name="Name", key="name", editable=True),
            Details(name="Collection",
                    key="collection_name"),
            Details(name="Project",
                    key="project_name"),
            Details(name="Barcode", key="barcode", editable=True),
            Details(name="Originals Received Date", key="originals_rec_date"),
            Details(
                name="Originals Returned Date",
                key="originals_return_date"),
            Details(name="Contact", key="contact"),
        ]

        selected_object = self._data_connector.get(serialize=True,
                                                   id=entity_id)

        collection = selected_object.get('collection')
        if collection is not None:
            collection_id = selected_object['collection'].get('collection_id')
            if collection_id is not None:

                collection_url = \
                    f"{url_for('page_collections')}/{collection_id}"

                selected_object['collection_url'] = collection_url

            collection_name = \
                selected_object['collection'].get('collection_name')

            if collection_name is not None:
                selected_object['collection_name'] = collection_name

        valid_note_types = []
        for note_type in self._data_connector.get_note_types():
            valid_note_types.append((note_type.name, note_type.id))

        project = selected_object.get('project')

        if project is not None:
            project_name = project['title']
            project_id = project['project_id']
            selected_object['project_name'] = project_name
            selected_object['project_id'] = project_id

        if "show_bread_crumb" in kwargs and kwargs["show_bread_crumb"] is True:
            breadcrumbs = self.build_breadcrumbs(
                "Object",
                project_url=url_for(
                    "page_project_details",
                    project_id=project['project_id']
                ),
                object_url=url_for(
                    "page_project_object_details",
                    project_id=project['project_id'],
                    object_id=selected_object['object_id']
                )
            )
        else:
            breadcrumbs = None
        return self.render_page(
            template="object_details.html",
            edit=False,
            fields=fields,
            formats=self._data_provider.get_formats(serialize=True),
            api_path=url_for('object', object_id=entity_id),
            valid_note_types=valid_note_types,
            breadcrumbs=breadcrumbs,
            show_bread_crumb=kwargs.get("show_bread_crumb"),
            object=selected_object)

    def render_page(self, template="object_details.html", **context):
        context['itemType'] = "Object"
        new_context = self.build_header_context(
            current_item=self.entity_title,
            context=context
        )
        return render_template(template, **new_context)


class CollectiontFrontend(FrontendEntity):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.CollectionDataConnector(provider.db_session_maker)

    def list(self):
        return self.render_page(template="collections.html",
                                api_path="api/collection",
                                row_table="collections"
                                )

    def display_details(self, entity_id, *args, **kwargs):
        selected_object = self._data_connector.get(serialize=True,
                                                   id=entity_id)

        return self.render_page(template="collection_details.html",
                                itemType="Collection",
                                api_path=url_for(
                                    "collection", collection_id=entity_id),
                                collection=selected_object)

    @property
    def entity_title(self) -> str:
        return "Collections"

    @property
    def entity_rule(self) -> str:
        return "/collection"

    @property
    def entity_list_page_name(self) -> str:
        return "page_collections"


class NewCollectionForm(AbsFrontend):

    def render_page(self, template="form_new_collection.html", **context):
        return render_template(template)
