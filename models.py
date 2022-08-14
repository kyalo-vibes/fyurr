from flask_sqlalchemy import SQLAlchemy
from app import db

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))

    website = db.Column(db.String(120))
    searching_venue = db.Column(db.Boolean, default=False)
    desc = db.Column(db.String, nullable=True)
    upcoming_shows = db.Column(db.String(120))
    past_shows = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'Venue {self.id} {self.name}'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    searching_artist = db.Column(db.Boolean, default=False)
    desc = db.Column(db.String, nullable=True)
    upcoming_shows = db.Column(db.String(120))
    past_shows = db.Column(db.String(120))
    artist_shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self) -> str:
        return f'Artist {self.id} {self.name}'


# Run the first time to create tables in the DB,
# then SQLAlchemy takes over from there
# db.create_all()


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('artists.id'),
        nullable=False)
    venue_id = db.Column(db.Integer,
                         db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f'Show {self.id} {self.artist_id} {self.venue_id}'
