from datetime import datetime

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flask_app import app

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

artist_genres_table = db.Table('ArtistGenres',
                               db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                               db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
                               )

venue_genres_table = db.Table('VenueGenres',
                              db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                              db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
                              )


class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Show(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, ForeignKey('Artist.id'), nullable=False)

    @property
    def artist_name(self):
        artist = Artist.query.filter_by(id=self.artist_id).first()
        return artist.name

    @property
    def artist_image_link(self):
        artist = Artist.query.filter_by(id=self.artist_id).first()
        return artist.image_link

    @property
    def venue_name(self):
        venue = Venue.query.filter_by(id=self.venue_id).first()
        return venue.name

    @property
    def venue_image_link(self):
        venue = Venue.query.filter_by(id=self.venue_id).first()
        return venue.image_link

    def serialize(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist_name,
            'artist_image_link': self.artist_image_link,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def serialize_for_artist(self):
        return {
            "venue_id": self.venue_id,
            "venue_name": self.venue_name,
            "venue_image_link": self.venue_image_link,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def serialize_for_all_upcoming_shows_page(self):
        return {
            "venue_id": self.id,
            "venue_name": self.venue_name,
            "artist_id": self.artist_id,
            "artist_name": self.artist_name,
            "artist_image_link": self.artist_image_link,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))

    genres = relationship("Genre", secondary=venue_genres_table)
    shows = relationship("Show", backref="venue")

    def __repr__(self):
        return f"Venue(id={self.id}, name={self.name}, address={self.address}, city={self.city}, state={self.state}," \
               f" phone={self.phone}, website={self.website}, facebook_link={self.facebook_link}, " \
               f"seeking_talent={self.seeking_talent}, seeking_description={self.seeking_description}, " \
               f"image_link={self.image_link}, genres={self.genres}, shows={self.shows})"

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def past_shows(self):
        return [show.serialize() for show in self.shows if show.start_time < datetime.now()]

    @property
    def upcoming_shows(self):
        return [show.serialize() for show in self.shows if show.start_time > datetime.now()]

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": [genre.name for genre in self.genres],
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": self.past_shows,
            "upcoming_shows": self.upcoming_shows,
            "past_shows_count": self.past_shows_count,
            "upcoming_shows_count": self.upcoming_shows_count
        }


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))

    genres = relationship("Genre", secondary=artist_genres_table)
    shows = relationship("Show")

    @property
    def past_shows(self):
        return [show.serialize_for_artist() for show in self.shows if show.start_time < datetime.now()]

    @property
    def upcoming_shows(self):
        return [show.serialize_for_artist() for show in self.shows if show.start_time > datetime.now()]

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": [genre.name for genre in self.genres],
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": self.past_shows,
            "upcoming_shows": self.upcoming_shows,
            "past_shows_count": self.past_shows_count,
            "upcoming_shows_count": self.upcoming_shows_count,
        }
