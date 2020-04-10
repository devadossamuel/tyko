"""added files table

Revision ID: 364bf8893123
Revises: a6f912f5e00f
Create Date: 2020-04-06 09:49:13.635961

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
# revision identifiers, used by Alembic.
revision = '364bf8893123'
down_revision = 'a6f912f5e00f'
branch_labels = None
depends_on = None


Base = declarative_base()

object_has_notes_table = sa.Table(
    "object_has_notes",
    Base.metadata,
    sa.Column("notes_id", sa.Integer, sa.ForeignKey("notes.note_id")),
    sa.Column("object_id", sa.Integer, sa.ForeignKey("object.object_id"))
)

item_has_notes_table = sa.Table(
    "item_has_notes",
    Base.metadata,
    sa.Column("notes_id", sa.Integer, sa.ForeignKey("notes.note_id")),
    sa.Column("item_id", sa.Integer, sa.ForeignKey("item.item_id"))
)


project_has_notes_table = sa.Table(
    "project_has_notes",
    Base.metadata,
    sa.Column("notes_id", sa.Integer, sa.ForeignKey("notes.note_id")),
    sa.Column("project_id", sa.Integer, sa.ForeignKey("project.project_id"))
)

class Treatment(Base):
    __tablename__ = "treatment"
    id = sa.Column(
        "treatment_id", sa.Integer, primary_key=True, autoincrement=True)

    needed = sa.Column("needed", sa.Text)
    given = sa.Column("given", sa.Text)
    date = sa.Column("date", sa.Date)
    item_id = sa.Column(sa.Integer, sa.ForeignKey("item.item_id"))

class NoteTypes(Base):
    __tablename__ = "note_types"
    id = sa.Column(
        "note_types_id", sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column("type_name", sa.Text)

class Note(Base):
    __tablename__ = "notes"

    id = sa.Column("note_id", sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column("text", sa.Text, nullable=False)

    note_type_id = sa.Column(
        sa.Integer, sa.ForeignKey("note_types.note_types_id"))

    note_type = orm.relationship("NoteTypes", foreign_keys=[note_type_id])


class ProjectStatus(Base):
    __tablename__ = "project_status_type"

    id = sa.Column("project_status_id",
                   sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column("name", sa.Text)


class Project(Base):
    __tablename__ = "project"

    id = sa.Column(
        "project_id",
        sa.Integer,
        primary_key=True,
        autoincrement=True)

    project_code = sa.Column("project_code", sa.Text)
    title = sa.Column("title", sa.Text)
    current_location = sa.Column("current_location", sa.Text)
    status = orm.relationship("ProjectStatus")
    status_id = sa.Column(
        sa.Integer, sa.ForeignKey("project_status_type.project_status_id"))
    specs = sa.Column("specs", sa.Text)

    notes = orm.relationship(
        "Note",
        secondary=project_has_notes_table,
        backref="project_sources"
    )

    objects = orm.relationship(
        "CollectionObject",
        backref="object_source"
    )

class Contact(Base):
    __tablename__ = "contact"

    id = sa.Column(
        "contact_id",
        sa.Integer,
        primary_key=True,
        autoincrement=True)

    first_name = sa.Column("first_name", sa.Text)
    last_name = sa.Column("last_name", sa.Text)
    email_address = sa.Column("email_address", sa.Text)


class Collection(Base):
    __tablename__ = "collection"
    id = sa.Column(
        "collection_id",
        sa.Integer,
        primary_key=True,
        autoincrement=True)
    record_series = sa.Column("record_series", sa.Text)
    collection_name = sa.Column("collection_name", sa.Text)
    department = sa.Column("department", sa.Text)
    contact = orm.relationship("Contact")
    contact_id = sa.Column(sa.Integer, sa.ForeignKey("contact.contact_id"))


class FormatTypes(Base):
    __tablename__ = "format_types"

    id = sa.Column(
        "format_id", sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column("name", sa.Text)


class CollectionObject(Base):
    __tablename__ = "object"

    id = sa.Column(
        "object_id",
        sa.Integer,
        primary_key=True,
        autoincrement=True)

    name = sa.Column("name", sa.Text)
    barcode = sa.Column("barcode", sa.Text)
    collection_id = \
        sa.Column(sa.Integer, sa.ForeignKey("collection.collection_id"))

    collection = orm.relationship("Collection", foreign_keys=[collection_id])

    project_id = sa.Column(sa.Integer, sa.ForeignKey("project.project_id"))
    project = orm.relationship("Project", foreign_keys=[project_id])
    originals_rec_date = sa.Column("originals_rec_date", sa.Date)
    originals_return_date = sa.Column("originals_return_date", sa.Date)
    notes = orm.relationship("Note",
                         secondary=object_has_notes_table,
                         backref="object_sources"
                         )

    items = orm.relationship("CollectionItem", backref="item_id")

    contact_id = sa.Column(sa.Integer, sa.ForeignKey("contact.contact_id"))

    contact = orm.relationship("Contact", foreign_keys=[contact_id])

class CollectionItem(Base):
    __tablename__ = "item"

    id = sa.Column("item_id", sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column("name", sa.Text)
    #
    file_name = sa.Column("file_name", sa.Text)
    medusa_uuid = sa.Column("medusa_uuid", sa.Text)

    collection_object_id = sa.Column("object_id",
                                     sa.Integer,
                                     sa.ForeignKey("object.object_id"),
                                     )

    collection_object = orm.relationship("CollectionObject",
                                     foreign_keys=[collection_object_id])

    obj_sequence = sa.Column("obj_sequence", sa.Integer)
    notes = orm.relationship("Note",
                         secondary=item_has_notes_table,
                         backref="item_sources"
                         )

    treatment = orm.relationship("Treatment", backref="treatment_id")

    format_type_id = sa.Column(sa.Integer,
                               sa.ForeignKey("format_types.format_id"))

    format_type = orm.relationship("FormatTypes", foreign_keys=[format_type_id])


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instantiation_files',
    sa.Column('file_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_name', sa.Text(), nullable=False),
    sa.Column('source', sa.Text(), nullable=True),
    sa.Column('generation', sa.Text(), nullable=True),
    sa.Column('filesize', sa.Integer(), nullable=True),
    sa.Column('filesize_unit', sa.Text(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.item_id'], ),
    sa.PrimaryKeyConstraint('file_id')
    )
    op.create_table('file_annotations',
    sa.Column('annotation_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['instantiation_files.file_id'], ),
    sa.PrimaryKeyConstraint('annotation_id')
    )
    op.create_table('file_notes',
    sa.Column('annotation_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('note', sa.Text(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['instantiation_files.file_id'], ),
    sa.PrimaryKeyConstraint('annotation_id')
    )
    # #################################333
    connection = op.get_bind()
    try:
        connection.execute('''
        INSERT INTO instantiation_files (file_name, item_id) 
        SELECT file_name, item_id 
        FROM item WHERE file_name is not null;'''
        )
    except sa.exc.IntegrityError:
        op.drop_table('file_annotations')
        op.drop_table('file_notes')
        op.drop_table('instantiation_files')
        raise
    with op.batch_alter_table("item") as batch_op:
        batch_op.drop_column( 'file_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('file_name', sa.TEXT(), nullable=True))
    connection = op.get_bind()
    joining_sql = """UPDATE item 
    SET file_name = (
        SELECT GROUP_CONCAT(file_name) 
        FROM instantiation_files 
        WHERE item.item_id = instantiation_files.item_id
        GROUP BY source)
    WHERE EXISTS(
        SELECT GROUP_CONCAT(file_name)
        FROM instantiation_files
        WHERE item.item_id = instantiation_files.item_id
        GROUP BY source)"""

    connection.execute(joining_sql)
    op.drop_table('file_notes')
    op.drop_table('file_annotations')
    op.drop_table('instantiation_files')
    ### end Alembic commands ###
