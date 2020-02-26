# pylint: disable=invalid-name

import abc
from typing import Tuple, Set, Optional, Callable, List
from dataclasses import dataclass

from flask import make_response, render_template, url_for

from . import data_provider
from .decorators import authenticate


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

        def filter_valid_entities_only(entity) -> bool:
            if entity[0] not in entity_menu:
                return False
            return True

        new_context["entities"] = filter(filter_valid_entities_only,
                                         FrontendEntity.all_entities())

        form_list = set()

        for entity_name in entity_menu:
            if current_item == entity_name:
                new_context["is_entity"] = True
                break
        else:
            new_context["is_entity"] = False

        for form in all_forms:
            form_list.add((form.form_title, form.form_page_name))

        new_context["all_forms"] = sorted(form_list, key=lambda x: [0])
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
            ("New Collection", "page_new_collection"),
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

    def render_page(self, template="newentity.html", **context):
        new_context = self.build_header_context(
            current_item=self.entity_title,
            context=context
        )

        return render_template(template, **new_context)

    @property
    @abc.abstractmethod
    def entity_title(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def entity_rule(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def entity_list_page_name(self) -> str:
        pass

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


class ProjectFrontend(FrontendEditable):

    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ProjectDataConnector(provider.db_session_maker)

    def list(self):
        return self.render_page(template="projects.html",
                                api_path="api/project",
                                row_table="projects"
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

        collections = data_provider.CollectionDataConnector(
            self._data_connector.session_maker).get(serialize=True)

        return self.render_page(
            template="project_details.html",
            project=selected_project,
            api_path=f"{url_for('.page_index')}api/project/{entity_id}",
            edit_link=edit_link,
            project_id=entity_id,
            valid_note_types=valid_note_types,
            fields=fields,
            collections=collections
            )

    def edit_details(self, entity_id):
        selected_project = self._data_connector.get(
            serialize=True, id=entity_id)[0]

        api_path = f"{url_for('.page_index')}api/project/{entity_id}"
        view_details_path = f"{url_for('page_projects')}/{entity_id}"

        return self.render_page(template="project_details.html",
                                project=selected_project,
                                api_path=api_path,
                                view_details_path=view_details_path,
                                edit=True)

    def create(self):
        return self.render_page(template="new_project.html",
                                api_path="/api/project/",
                                title="New Project",
                                on_success_redirect_base="/project/",
                                )

    def render_page(self, template="project_details.html", **context):
        context['itemType'] = "Project"
        return super().render_page(template, **context)


class ItemFrontend(FrontendEntity):
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

        valid_note_types = []
        for note_type in self._data_connector.get_note_types():
            valid_note_types.append((note_type.name, note_type.id))
        return self.render_page(template="item_details.html",
                                project_id=kwargs.get("project_id"),
                                valid_note_types=valid_note_types,
                                object_id=kwargs.get("object_id"),
                                fields=fields,
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


class ObjectFrontend(FrontendEditable):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

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

    def edit_details(self, entity_id):
        selected_object = self._data_connector.get(
            serialize=True, id=entity_id)[0]
        edit_link = f"{url_for('page_object')}/{entity_id}/edit"
        api_path = f"{url_for('.page_index')}api/object/{entity_id}"
        view_details_path = f"{url_for('page_object')}/{entity_id}"
        return self.render_page(template="object_details.html",
                                object=selected_object,
                                api_path=api_path,
                                view_details_path=view_details_path,
                                edit_link=edit_link,
                                edit=True)

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
        api_path = f"{url_for('.page_index')}api/object/{entity_id}"

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

        return self.render_page(template="object_details.html",
                                edit=False,
                                fields=fields,
                                api_path=api_path,
                                valid_note_types=valid_note_types,
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


class NewEntityForm(AbsFrontend):
    _forms: Set[Tuple[str, str]] = set()
    @classmethod
    def all_forms(cls):
        return sorted(cls._forms)

    @property
    @abc.abstractmethod
    def form_title(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def form_page_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def form_page_rule(self) -> str:
        pass

    def __init__(self):
        NewEntityForm._forms.add(
            (self.form_title, self.form_page_name)
        )

    @authenticate
    def render_page(self, template="newentity.html", **context):
        new_context = self.build_header_context(
            current_item=self.form_title,
            context=context
        )
        return render_template(template, **new_context)

    @abc.abstractmethod
    def create(self):
        pass


class NewProjectForm(NewEntityForm):

    @property
    def form_title(self) -> str:
        return "New Project"

    @property
    def form_page_name(self) -> str:
        return "page_new_project"

    def create(self):
        return self.render_page(
            form_title="New Project",
            api_location="api/project/",
            form_fields=[
                FormField("text", "title", "Project Title", True),
                FormField("text", "project_code", "Project Code", False),
                FormField("text", "status", "Project Status", False),
                FormField("text", "current_location", "Current Location",
                          False),
                FormField("text", "specs", "Specs", False),
            ],
        )

    @property
    def form_page_rule(self) -> str:
        return "/newproject"


class NewCollectionForm(NewEntityForm):

    @property
    def form_title(self) -> str:
        return "New Collection"

    @property
    def form_page_name(self) -> str:
        return "page_new_collection"

    @property
    def form_page_rule(self) -> str:
        return "/newcollection"

    def create(self):
        return self.render_page(
            form_title="New Collection",
            api_location="api/collection/",
            form_fields=[
                FormField("text", "collection_name", "Name", True),
                FormField("text", "department", "Department", True),
            ]
        )


class NewItemForm(NewEntityForm):

    @property
    def form_title(self) -> str:
        return "New Item"

    @property
    def form_page_name(self) -> str:
        return "page_new_item"

    @property
    def form_page_rule(self) -> str:
        return "/newitem"

    def create(self):
        return self.render_page(
            form_title="New Item",
            api_location="api/item/",
            form_fields=[
                FormField("text", "name", "Name", True),
                FormField("text", "file_name", "File name", False),
            ]
        )


class NewObjectForm(NewEntityForm):

    @property
    def form_title(self) -> str:
        return "New Object"

    @property
    def form_page_name(self) -> str:
        return "page_new_object"

    @property
    def form_page_rule(self) -> str:
        return "/newobject"

    def create(self):
        return self.render_page(
            form_title="New Object",
            api_location="api/object/",
            form_fields=[
                FormField("text", "name", "Name", True),
                FormField("text", "barcode", "Barcode", False),
            ]
        )


all_forms = {
    NewCollectionForm(),
    NewItemForm(),
    NewObjectForm()
}
