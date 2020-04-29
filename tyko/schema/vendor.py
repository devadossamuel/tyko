from typing import Dict, List, Mapping

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData

vendor_has_contacts_table = db.Table(
    "vendor_has_contacts",
    AVTables.metadata,
    db.Column("contact_id", db.Integer, db.ForeignKey("contact.contact_id")),
    db.Column("vendor_id", db.Integer, db.ForeignKey("vendor.vendor_id"))
)


class Vendor(AVTables):
    __tablename__ = "vendor"

    id = db.Column(
        "vendor_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)
    address = db.Column("address", db.Text)
    city = db.Column("city", db.Text)
    state = db.Column("state", db.Text)
    zipcode = db.Column("zipcode", db.Text)
    contacts = relationship("Contact",
                            secondary=vendor_has_contacts_table,
                            backref="vendor_id"
                            )

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        contacts: List[Mapping[str, SerializedData]] = [
            contact.serialize() for contact in self.contacts
        ]
        data: Dict[str, SerializedData] = {
            "vendor_id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
            "contacts": contacts,
        }
        return data


vendor_transfer_has_an_object = db.Table(
    "vendor_transfer_has_an_object",
    AVTables.metadata,
    db.Column("object_id",
              db.Integer,
              db.ForeignKey("tyko_object.object_id")),
    db.Column("vendor_transfer_id",
              db.Integer,
              db.ForeignKey("vendor_transfer.vendor_transfer_id")
              )
)


class VendorTransfer(AVTables):
    __tablename__ = "vendor_transfer"

    id = db.Column(
        "vendor_transfer_id", db.Integer, primary_key=True, autoincrement=True)

    vendor_id = db.Column(
        db.Integer, db.ForeignKey("vendor.vendor_id")
    )
    vendor = relationship("Vendor", foreign_keys=[vendor_id])

    # date the digital surrogates and accompanying metadata was received
    # from vendor
    vendor_deliverables_rec_date = \
        db.Column("vendor_deliverables_rec_date", db.Date)

    # date the originals were returned from the vendor
    returned_originals_rec_date = \
        db.Column("returned_originals_rec_date", db.Date)

    transfer_objects = relationship(
        "CollectionObject",
        secondary=vendor_transfer_has_an_object,
        backref="transfer_object"
    )

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "vendor_transfer_id": self.id,
            "vendor_id": self.vendor_id,
            "vendor_deliverables_rec_date":
                self.serialize_date(self.vendor_deliverables_rec_date),
            "returned_originals_rec_date":
                self.serialize_date(self.returned_originals_rec_date)
        }
