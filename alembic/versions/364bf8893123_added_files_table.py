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


def add_sample_record():
    connection = op.get_bind()
    connection.execute('''
                   INSERT INTO collection (collection_name, department)
                   VALUES ("Sample collection", "Preservation Department")
                   ''')

    connection.execute('''
        INSERT INTO project (project_code, title, current_location)
        VALUES ("SAMP120", "Sample Project", "Room 425")
    ''')

    connection.execute('''
        INSERT INTO object (
            name, 
            collection_id, 
            project_id,
            barcode, 
            originals_rec_date, 
            originals_return_date
            )
        VALUES ("Anderson, Jim, 28 March 1998", 
            (
                SELECT collection_id 
                FROM collection 
                WHERE collection_name = "Sample collection"
            ), 
            (
                SELECT project_id 
                FROM project 
                WHERE title = "Sample Project"
            ),
            "SAMPLE0002",
            "2019-10-20",
            "2019-11-25"
        )
    ''')

    connection.execute('''
            INSERT INTO item (
                name, 
                obj_sequence, 
                object_id
                )
            VALUES (
                "Anderson, Jim, 28 March 1998, Tape 1", 
                "1", 
                (
                    SELECT object_id 
                    FROM object 
                    WHERE name = "Anderson, Jim, 28 March 1998"
                )
            ) 
    ''')

    # =========================================================================
    # Preservation File
    # =========================================================================
    connection.execute('''
        INSERT INTO instantiation_files (
                file_name, 
                generation, 
                item_id
                )
            VALUES (
                "4130178_Box1_AndersonJim_1998Mar28_Tape1_a_96.wav",
                "Preservation",
                (
                    SELECT item_id
                    FROM item
                    WHERE name = "Anderson, Jim, 28 March 1998, Tape 1"
                )
                
            )
    ''')
    connection.execute('''
        INSERT INTO file_annotations (
           file_id, 
           type_id, 
           content
           )
        VALUES (
            (
                SELECT file_id
                FROM instantiation_files
                WHERE file_name = "4130178_Box1_AndersonJim_1998Mar28_Tape1_a_96.wav"
            ),
            (
                SELECT type_id 
                FROM file_annotation_types
                WHERE name = "Encode Software Name" 
            ),
       "Nuendo"
       )
       ''')
    # =========================================================================
    # Access File
    # =========================================================================


    connection.execute('''
                INSERT INTO instantiation_files (
                    file_name, 
                    generation, 
                    item_id
                    )
                VALUES (
                    "4130178_Box1_AndersonJim_1998Mar28_Tape1_a.mp3",
                    "Access",
                    (
                        SELECT item_id
                        FROM item
                        WHERE name = "Anderson, Jim, 28 March 1998, Tape 1"
                    )

                )
    ''')

    connection.execute('''
        INSERT INTO file_annotations (
            file_id,
            type_id,
            content
            )
        VALUES (
            (
                SELECT file_id
                FROM instantiation_files
                WHERE file_name = "4130178_Box1_AndersonJim_1998Mar28_Tape1_a.mp3"
            ),
            (
                SELECT type_id 
                FROM file_annotation_types
                WHERE name = "Encode Software Name" 
            ),
            "Wavelab"
            )
    ''')


def remove_sample_record():
    connection = op.get_bind()
    connection.execute('''
        DELETE FROM collection WHERE collection_name="Sample collection";
        ''')

    connection.execute('''
        DELETE FROM project WHERE title="Sample Project";
        ''')

    connection.execute('''
        DELETE FROM object WHERE name ="Anderson, Jim, 28 March 1998"
    ''')

    connection.execute('''
        DELETE FROM item WHERE name ="Anderson, Jim, 28 March 1998, Tape 1"
    ''')

    # =========================================================================
    # Preservation File
    # =========================================================================
    connection.execute('''
            DELETE FROM file_annotations
            WHERE file_id IN (
                SELECT instantiation_files.file_id
                FROM instantiation_files
                INNER JOIN file_annotations
                ON (instantiation_files.file_id = file_annotations.file_id)
                WHERE(file_name ="4130178_Box1_AndersonJim_1998Mar28_Tape1_a_96.wav")
            )
        ''')

    connection.execute('''
        DELETE FROM instantiation_files 
        WHERE file_name ="4130178_Box1_AndersonJim_1998Mar28_Tape1_a_96.wav"
    ''')

    # =========================================================================
    # Access File
    # =========================================================================

    connection.execute('''
            DELETE FROM instantiation_files 
            WHERE file_name ="4130178_Box1_AndersonJim_1998Mar28_Tape1_a.mp3"
        ''')

    connection.execute('''
                DELETE FROM file_annotations
                WHERE file_id IN (
                    SELECT instantiation_files.file_id
                    FROM instantiation_files
                    INNER JOIN file_annotations
                    ON (instantiation_files.file_id = file_annotations.file_id)
                    WHERE(file_name = "4130178_Box1_AndersonJim_1998Mar28_Tape1_a.mp3")
                )
            ''')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        upgrade_schema()
        add_sample_record()
    except sa.exc.OperationalError:
        conn = op.get_bind()
        inspector = sa.engine.reflection.Inspector.from_engine(conn)
        tables = inspector.get_table_names()
        added_tables = [
            "file_annotations",
            "file_annotation_types",
            "file_notes",
            "instantiation_files",
        ]
        for table in added_tables:
            if table in tables:
                op.drop_table(table)
        raise
    except sa.exc.IntegrityError:
        op.drop_table('file_annotations')
        op.drop_table('file_annotation_types')
        op.drop_table('file_notes')
        op.drop_table('instantiation_files')
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
        connection = op.get_bind()
        connection.execute(joining_sql)
        raise

    # ### end Alembic commands ###


def migrate_to_file_tables(connection):
    connection.execute('''
    INSERT INTO instantiation_files (file_name, item_id) 
    SELECT file_name, item_id 
    FROM item WHERE file_name is not null;'''
                       )
    with op.batch_alter_table("item") as batch_op:
        batch_op.drop_column('file_name')


def upgrade_schema():
    add_new_tables()
    connection = op.get_bind()
    migrate_to_file_tables(connection)


def add_new_tables():
    op.create_table('instantiation_files',
                    sa.Column('file_id', sa.Integer(), autoincrement=True,
                              nullable=False),
                    sa.Column('file_name', sa.Text(), nullable=False),
                    sa.Column('source', sa.Text(), nullable=True),
                    sa.Column('generation', sa.Text(), nullable=True),
                    sa.Column('filesize', sa.Integer(), nullable=True),
                    sa.Column('filesize_unit', sa.Text(), nullable=True),
                    sa.Column('item_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['item_id'],
                                            ['item.item_id'], ),
                    sa.PrimaryKeyConstraint('file_id')
                    )
    annotation_table = op.create_table('file_annotation_types',
                                       sa.Column('type_id', sa.Integer(),
                                                 autoincrement=True,
                                                 nullable=False),
                                       sa.Column('name', sa.Text(),
                                                 nullable=False),
                                       sa.Column("active", sa.Boolean,
                                                 nullable=False,
                                                 default=True),
                                       sa.PrimaryKeyConstraint('type_id')
                                       )
    op.bulk_insert(
        annotation_table,
        [
            {"name": "Source Deck Type"},
            {"name": "Audio Quality"},
            {"name": "Encode Software Name"}

        ]
    )
    
    op.create_table('file_annotations',
                    sa.Column('annotation_id', sa.Integer(), autoincrement=True,
                              nullable=False),
                    sa.Column('file_id', sa.Integer(), nullable=True),
                    sa.Column('type_id', sa.Integer(), nullable=False),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['file_id'],
                                            ['instantiation_files.file_id'], ),
                    sa.ForeignKeyConstraint(['type_id'], [
                        'file_annotation_types.type_id'], ),
                    sa.PrimaryKeyConstraint('annotation_id')
                    )
    
    op.create_table('file_notes',
                    sa.Column('note_id', sa.Integer(), autoincrement=True,
                              nullable=False),
                    sa.Column('message', sa.Text(), nullable=False),
                    sa.Column('file_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['file_id'],
                                            ['instantiation_files.file_id'], ),
                    sa.PrimaryKeyConstraint('note_id')
                    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    remove_sample_record()
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
    op.drop_table('file_annotation_types')
    op.drop_table('instantiation_files')

    ### end Alembic commands ###
