import logging

import babel
from babel.dates import get_timezone
import dateutil.parser
from flask import render_template, request, flash, redirect, url_for

from flask_app import app
from forms import VenueForm, ArtistForm, ShowForm
from models import Venue, Artist, Genre, Show, db

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
        _edit_or_create_db_item(new_venue, request.form)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(e)
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


def _edit_or_create_db_item(db_item, form):
    """Used to create a new artist, venue, or show."""
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
    _edit_or_create_db_item(artist, request.form)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    _edit_or_create_db_item(venue, request.form)
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
    _edit_or_create_db_item(new_artist, request.form)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays all shows
    all_shows = Show.query.all()
    data = [show.serialize_for_all_upcoming_shows_page() for show in all_shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    new_show = Show()
    _edit_or_create_db_item(new_show, request.form)
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = logging.FileHandler('error.log')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
