import abc

from flask import make_response, render_template
import avforms.data_provider
from typing import Tuple, Set
from dataclasses import dataclass
from .decorators import authenticate


@dataclass
class FormField:
    form_type: str
    form_id: str
    form_user_text: str
    required: bool


class AbsFrontend(metaclass=abc.ABCMeta):
    def build_header_context(self, current_item, context):
        context["selected_menu_item"] = current_item
        context["entities"] = FrontendEntity.all_entities()
        form_list = set()

        for form in all_forms:
            form_list.add((form.form_title, form.form_page_name))

        context["all_forms"] = sorted(form_list)

    @abc.abstractmethod
    def _render_page(self, tempate, **context):
        pass


class FrontendEntity(AbsFrontend):
    _entities: Set[Tuple[str, str]] = {("Formats", "page_formats")}

    def __init__(self, provider: avforms.data_provider.DataProvider) -> None:
        self._data_provider = provider

        FrontendEntity._entities.add(
            (self.entity_title, self.entity_list_page_name)
        )

    def list(self):
        return make_response("not implimented", 404)

    def _render_page(self, tempate, **context):
        self.build_header_context(
            current_item=self.entity_title,
            context=context
        )

        return render_template(tempate, **context)

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
        return sorted(cls._entities)


class ProjectFrontend(FrontendEntity):

    def list(self):
        projects = self._data_provider.entities["project"].get(serialize=False)
        return self._render_page(tempate="projects.html", projects=projects)

    @property
    def entity_title(self) -> str:
        return "Project"

    @property
    def entity_rule(self) -> str:
        return "/project"

    @property
    def entity_list_page_name(self) -> str:
        return "page_projects"


class ItemFrontend(FrontendEntity):
    def list(self):
        items = self._data_provider.entities['item'].get(serialize=False)
        return self._render_page(tempate="items.html", items=items)

    @property
    def entity_title(self) -> str:
        return "Item"

    @property
    def entity_rule(self) -> str:
        return "/item"

    @property
    def entity_list_page_name(self) -> str:
        return "page_item"


class ObjectFrontend(FrontendEntity):
    def list(self):
        objects = self._data_provider.entities['object'].get(serialize=False)
        return self._render_page(tempate="objects.html", objects=objects)

    @property
    def entity_title(self) -> str:
        return "Objects"

    @property
    def entity_rule(self) -> str:
        return "/object"

    @property
    def entity_list_page_name(self) -> str:
        return "page_object"


class CollectiontFrontend(FrontendEntity):
    def list(self):
        collections = \
            self._data_provider.entities["collection"].get(serialize=False)

        return self._render_page(tempate="collections.html",
                                 collections=collections)

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
    def _render_page(self, **context):
        self.build_header_context(
            current_item=self.form_title,
            context=context
        )
        return render_template("newentity.html", **context)

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
        return self._render_page(
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
        return self._render_page(
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
        return self._render_page(
            form_title="New Item",
            api_location="api/item/",
            form_fields=[
                FormField("text", "name", "Name", True),
                FormField("text", "barcode", "Barcode", True),
                FormField("text", "file_name", "File name", True),
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
        return self._render_page(
            form_title="New Object",
            api_location="api/object/",
            form_fields=[
                FormField("text", "name", "Name", True),
            ]
        )


all_forms = {
    NewProjectForm(),
    NewCollectionForm(),
    NewItemForm(),
    NewObjectForm()
}
