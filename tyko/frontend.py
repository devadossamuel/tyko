# pylint: disable=invalid-name

import abc
from typing import Tuple, Set
from dataclasses import dataclass

from flask import make_response, render_template
from . import data_provider, scheme
from .decorators import authenticate


@dataclass
class FormField:
    form_type: str
    form_id: str
    form_user_text: str
    required: bool


class AbsFrontend(metaclass=abc.ABCMeta):
    @classmethod
    def build_header_context(cls, current_item, context):
        entity_menu = [
            "Collections",
            "Items",
            "Objects"
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


class FrontendEntity(AbsFrontend):
    _entities: Set[Tuple[str, str]] = {
        # ("Formats", "page_formats"),
        ("Items", "page_item"),
        ("Objects", "page_object"),
    }

    def __init__(self, provider: data_provider.DataProvider) -> None:
        self._data_provider = provider

        FrontendEntity._entities.add(
            (self.entity_title, self.entity_list_page_name)
        )

    def display_details(self, entity_id):  # pylint: disable=unused-argument
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


class ProjectFrontend(FrontendEntity):

    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ProjectDataConnector(provider.db_session_maker)

    def list(self):
        projects = self._data_connector.get(serialize=True)
        return self.render_page(template="projects.html", projects=projects)

    @property
    def entity_title(self) -> str:
        return "Projects"

    @property
    def entity_rule(self) -> str:
        return "/project"

    @property
    def entity_list_page_name(self) -> str:
        return "page_projects"

    def display_details(self, entity_id):
        selected_project = self._data_connector.get(
            serialize=True, id=entity_id)[0]

        return self.render_page(template="project_details.html",
                                project=selected_project)


class ItemFrontend(FrontendEntity):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ItemDataConnector(provider.db_session_maker)

    def list(self):
        items = []

        for item in self._data_connector.get(serialize=True):

            # # replace the format id with format string name
            for k, v in scheme.format_types.items():
                if v[0] == item["format_type_id"]:
                    item['format_type'] = k
                    break
            items.append(item)
        return self.render_page(template="items.html", items=items)

    def display_details(self, entity_id):
        selected_item = self._data_connector.get(
            serialize=True, id=entity_id)[0]

        for k, v in scheme.format_types.items():
            if v[0] == selected_item["format_type_id"]:
                selected_item['format_type'] = k
                break
        return self.render_page(template="item_details.html",
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


class ObjectFrontend(FrontendEntity):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.ObjectDataConnector(provider.db_session_maker)

    def list(self):
        objects = self._data_connector.get(serialize=False)
        return self.render_page(template="objects.html", objects=objects)

    @property
    def entity_title(self) -> str:
        return "Objects"

    @property
    def entity_rule(self) -> str:
        return "/object"

    @property
    def entity_list_page_name(self) -> str:
        return "page_object"

    def display_details(self, entity_id):

        selected_object = self._data_connector.get(serialize=True,
                                                   id=entity_id)[0]

        return self.render_page(template="object_details.html",
                                object=selected_object)


class CollectiontFrontend(FrontendEntity):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        super().__init__(provider)

        self._data_connector = \
            data_provider.CollectionDataConnector(provider.db_session_maker)

    def list(self):
        collections = self._data_connector.get(serialize=True)

        return self.render_page(template="collections.html",
                                collections=collections)

    def display_details(self, entity_id):
        selected_object = self._data_connector.get(serialize=True,
                                                   id=entity_id)[0]

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
    NewProjectForm(),
    NewCollectionForm(),
    NewItemForm(),
    NewObjectForm()
}
