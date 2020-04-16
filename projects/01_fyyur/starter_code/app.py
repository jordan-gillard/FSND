# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from babel import default_locale
from babel.dates import get_timezone
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from config import SQLALCHEMY_DATABASE_URI
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

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


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
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


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, frmat='medium'):
    date = dateutil.parser.parse(value)
    if frmat == 'full':
        frmat = "EEEE MMMM, d, y 'at' h:mma"
    elif frmat == 'medium':
        frmat = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, frmat, tzinfo=get_timezone('US/Eastern'), locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_cities = set([(city, state) for city, state in [(venue.city, venue.state)
                                                        for venue in Venue.query.all()]])
    data = []
    for city, state in all_cities:
        venues_in_city_state = Venue.query.filter_by(state=state).filter_by(city=city).all()
        data.append({
            "city": city,
            "state": state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": venue.upcoming_shows_count
            } for venue in venues_in_city_state]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    found_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(found_venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.upcoming_shows_count,
        } for venue in found_venues]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('pages/show_venue.html', venue=venue.serialize())


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    data = request.form
    try:
        new_venue = Venue()
        _edit_or_create_venue_or_artist(new_venue, request.form)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully deleted!')
    except Exception as e:
        flash('An error occurred. The venue could not be deleted.')
        print(e)
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = [{
        "id": artist.id,
        "name": artist.name
    } for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    found_artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(found_artists),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.upcoming_shows_count,
        } for artist in found_artists]
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.filter_by(id=artist_id).first()
    return render_template('pages/show_artist.html', artist=artist.serialize())


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist.serialize())


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue.serialize())


def _edit_or_create_venue_or_artist(db_item, form):
    try:
        for key, value in form.items():
            if key.lower() != 'genres':
                setattr(db_item, key, value)
            else:
                genre = Genre.query.filter_by(name=value).first()
                db_item.genres = [genre]
        db.session.add(db_item)
        db.session.commit()
    except Exception as e:
        flash('An error occurred.')
        print(e)
        db.session.rollback()
    finally:
        db.session.close()


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    _edit_or_create_venue_or_artist(artist, request.form)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    _edit_or_create_venue_or_artist(venue, request.form)
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    new_artist = Artist()
    _edit_or_create_venue_or_artist(new_artist, request.form)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
