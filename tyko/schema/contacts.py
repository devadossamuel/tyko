from typing import Dict

import sqlalchemy as db

from tyko.schema.avtables import AVTables, SerializedData


class Contact(AVTables):
    __tablename__ = "contact"

    id = db.Column(
        "contact_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    first_name = db.Column("first_name", db.Text)
    last_name = db.Column("last_name", db.Text)
    email_address = db.Column("email_address", db.Text)

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "contact_id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address
        }
