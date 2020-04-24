import abc
import datetime
from typing import Union, List, Dict, Optional

from sqlalchemy.ext.declarative.api import DeclarativeMeta, declarative_base

SerializedData = \
    Union[int, str, List['SerializedData'], None, Dict[str, 'SerializedData']]


class DeclarativeABCMeta(DeclarativeMeta, abc.ABCMeta):
    pass


class AVTables(declarative_base(metaclass=DeclarativeABCMeta)):
    __abstract__ = True

    @abc.abstractmethod
    def serialize(self, recurse=False) -> Dict[str, SerializedData]:  # noqa: E501 pylint: disable=no-self-use
        """Serialize the data so that it can be turned into a JSON format"""
        return {}

    @classmethod
    def serialize_date(cls, date: Optional[datetime.date]):
        if isinstance(date, datetime.date):
            return date.isoformat()

        return None
