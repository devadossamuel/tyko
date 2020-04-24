# pylint: disable=too-few-public-methods, invalid-name
from sqlalchemy.orm import scoped_session, sessionmaker

from .projects import Project
from .contacts import Contact
from .collection import Collection
from .notes import Note
from .treatment import Treatment
from .vendor import Vendor, VendorTransfer
from .formats import GroovedDisc, Film, OpenReel
from .items import CollectionItem
from .objects import CollectionObject

ALEMBIC_VERSION: str = "364bf8893123"

Session = scoped_session(sessionmaker(expire_on_commit=False))

__all__ = [
    "Contact",
    "Collection",
    "CollectionItem",
    "CollectionObject",
    "Film",
    "GroovedDisc",
    "Note",
    "OpenReel",
    "Project",
    "Treatment",
    "Vendor",
    "VendorTransfer",
]
