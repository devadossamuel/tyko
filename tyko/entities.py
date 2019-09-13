import abc
from typing import NamedTuple, Type

from . import frontend
from . import middleware
from . import data_provider


class AbsFactory(metaclass=abc.ABCMeta):
    def __init__(self, provider: data_provider.DataProvider) -> None:
        self._data_provider = provider

    @abc.abstractmethod
    def middleware(self):
        """Middleware for the a given entity"""

    @abc.abstractmethod
    def web_frontend(self) -> frontend.FrontendEntity:
        """Web front tne for displaying the information in a browser"""


class EntityComponent(NamedTuple):
    factory: Type[AbsFactory]
    data_connector: Type[data_provider.AbsDataProviderConnector]


class ProjectFactory(AbsFactory):
    def middleware(self) -> middleware.AbsMiddlwareEntity:
        return middleware.ProjectMiddlwareEntity(self._data_provider)

    def web_frontend(self) -> frontend.FrontendEntity:
        return frontend.ProjectFrontend(self._data_provider)


class ItemFactory(AbsFactory):
    def middleware(self) -> middleware.AbsMiddlwareEntity:
        return middleware.ItemMiddlwareEntity(self._data_provider)

    def web_frontend(self) -> frontend.FrontendEntity:
        return frontend.ItemFrontend(self._data_provider)


class CollectionFactory(AbsFactory):

    def middleware(self):
        return middleware.CollectionMiddlwareEntity(self._data_provider)

    def web_frontend(self) -> frontend.FrontendEntity:
        return frontend.CollectiontFrontend(self._data_provider)


class ObjectFactory(AbsFactory):

    def middleware(self):
        return middleware.ObjectMiddlwareEntity(self._data_provider)

    def web_frontend(self) -> frontend.FrontendEntity:
        return frontend.ObjectFrontend(self._data_provider)


def load_entity(name, provider: data_provider.DataProvider) \
        -> AbsFactory:

    new_entity = all_entities[name][0](provider)

    return new_entity


all_entities = {
    "project": EntityComponent(
        factory=ProjectFactory,
        data_connector=data_provider.ProjectDataConnector
    ),
    "collection": EntityComponent(
        factory=CollectionFactory,
        data_connector=data_provider.CollectionDataConnector
    ),
    "item": EntityComponent(
        factory=ItemFactory,
        data_connector=data_provider.ItemDataConnector
    ),
    "object": EntityComponent(
        factory=ObjectFactory,
        data_connector=data_provider.ObjectDataConnector
    ),
}
