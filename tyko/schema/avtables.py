import abc
import datetime
import warnings
from typing import Union, List, Optional, Mapping

from sqlalchemy.ext.declarative.api import DeclarativeMeta, declarative_base

SerializedData = \
    Optional[Union[int,
                   str,
                   List['SerializedData'],
                   Mapping[str, 'SerializedData']]]


class DeclarativeABCMeta(DeclarativeMeta, abc.ABCMeta):
    pass


class AVTables(declarative_base(metaclass=DeclarativeABCMeta)):
    __abstract__ = True

    @abc.abstractmethod
    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:  # noqa: E501 pylint: disable=no-self-use
        """Serialize the data so that it can be turned into a JSON format"""
        return {}

    @classmethod
    def serialize_date(cls, date: Optional[datetime.date]):
        if isinstance(date, datetime.date):
            return date.isoformat()

        return None
