# pylint: disable=too-few-public-methods, invalid-name
from sqlalchemy.orm import scoped_session, sessionmaker

from .projects import Project, ProjectStatus
from .contacts import Contact
from .collection import Collection
from .notes import Note, NoteTypes
from .treatment import Treatment
from .vendor import Vendor, VendorTransfer
from .formats import GroovedDisc, Film, OpenReel, FormatTypes, AudioCassette, \
    CassetteType, CassetteTapeType, CassetteTapeThickness

from .items import CollectionItem
from .objects import CollectionObject
from .instantiation import FileAnnotationType, InstantiationFile, \
    FileAnnotation, FileNotes

ALEMBIC_VERSION: str = "364bf8893123"

Session = scoped_session(sessionmaker(expire_on_commit=False))

__all__ = [
    "AudioCassette",
    "CassetteTapeThickness",
    "CassetteTapeType",
    "CassetteType",
    "Contact",
    "Collection",
    "CollectionItem",
    "CollectionObject",
    "FileAnnotationType",
    "InstantiationFile",
    "FileNotes",
    "FileAnnotation",
    "Film",
    "FormatTypes",
    "GroovedDisc",
    "Note",
    "NoteTypes",
    "OpenReel",
    "Project",
    "ProjectStatus",
    "Treatment",
    "Vendor",
    "VendorTransfer",
]
