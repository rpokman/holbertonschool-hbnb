from app import db

# Association table for Place ↔ Amenity many-to-many relationship
place_amenity = db.Table('place_amenity',
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=db.func.now())
)
