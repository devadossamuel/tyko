from typing import Dict

import sqlalchemy as db

from tyko.schema.avtables import AVTables, SerializedData


class Treatment(AVTables):
    __tablename__ = "treatment"
    id = db.Column(
        "treatment_id", db.Integer, primary_key=True, autoincrement=True)

    needed = db.Column("needed", db.Text)
    given = db.Column("given", db.Text)
    date = db.Column("date", db.Date)
    item_id = db.Column(db.Integer, db.ForeignKey("formats.item_id"))

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "treatment_id": self.id,
            "needed": self.needed,
            "given": self.given,
            "date": self.serialize_date(self.date),
            "item_id": self.item_id
        }
