# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from dataclasses import dataclass
import json
from types import CoroutineType
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# configured in config.py
migrate = Migrate(app, db)
app.config["SECRET_KEY"] = "myKey"


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()

    return render_template('pages/home.html', venues=venues, artists=artists)



#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # num_upcoming_shows should be aggregated based on number of upcoming
    # shows per venue.

    areas = db.session.query(Venue.city,
                             Venue.state).distinct()  # get unique areas
    venue_data = []
    for location in areas:
        # first dictionary of city and state for grouping
        location = dict(zip(('city', 'state'), location))
        # second dictionary inside first dictionary to store venues in the
        # grouping
        location['venues'] = []
        venues_list = Venue.query.filter_by(
            city=location['city'], state=location['state']).all()
        for venue in venues_list:
            # fetch shows for the current venue
            shows = venue.id
            venue = {   # the second dictionary assignment
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows_venues(shows))
            }
            location['venues'].append(venue)
        venue_data.append(location)

    return render_template('pages/venues.html', areas=venue_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    response = {  # initialize response
        "data": []
    }
    # fetch all venue ids and names
    # venues = db.session.query(Venue.id, Venue.name).all()
    # fetch searching term
    s_term = request.form.get('search_term')
    # print(s_term)    # confirm searching term is fetched
    if not s_term:
        # error message for null searching term
        flash("You did not search for anything")
    elif s_term:
        venues = db.session.query(Venue.id, Venue.name).filter(
            Venue.name.ilike(f'%{s_term}%')).all()
        for venue in venues:
            id = venue.id
            name = venue.name   # assign venue id and name for current loop
            venue = {         # assign match venue id
                'id': id,     # and name to venue dictionary
                'name': name
            }
            # append match to response dictionary
            response['data'].append(venue)
        # count total matches in response dictionary
        response['count'] = len(response['data'])

# print used to confirm function is fetching,
# correct search term and giving correct response
# print(name.find(s_term))
# print(response)
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    # get venue data that matches the given venue id
    venue = Venue.query.filter_by(id=venue_id).first()
    # get shows data for the given venue
    shows = venue_id
    data = {    # assign data dictionary to values of the matched venue
        "name": venue.name,
        "id": venue.id,
        "genres": ''.join(list(filter(
            lambda x: x != '{' and x != '}',
            venue.genres))).split(','),
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.searching_venue,
        "seeking_description": venue.desc,
        "image_link": venue.image_link,
        "upcoming_shows": upcoming_shows_venues(shows),
        "upcoming_shows_count": len(upcoming_shows_venues(shows)),
        "past_shows": past_shows_venues(shows),
        "past_shows_count": len(past_shows_venues(shows))
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    if form.validate():   # run validators on form
        try:
            venue_data = Venue(   # assign form data to venue_data dictionary
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website=form.website_link.data,
                searching_venue=form.seeking_talent.data,
                desc=form.seeking_description.data
            )
            db.session.add(venue_data)
            db.session.commit()   # add record to db

        # on successful db insert, flash success
            # successful creation message
            flash(
                'Venue ' +
                request.form['name'] +
                ' was successfully listed!')
        except BaseException:
            print(sys.exc_info())
            flash(
                'An error occurred. Venue ' +
                request.form['name'] +
                ' could not be listed.')  # error message
            db.session.rollback()

        finally:
            db.session.close()
    else:
        flash(form.errors)  # error message for invalid data in form

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    # BONUS CHALLENGE: Implement a button to delete
    # a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # artists.html will fetch id and namefor the respective artists
    artists_data = Artist.query.all()
    return render_template('pages/artists.html', artists=artists_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    response = {    # initialize response dictionary
        "data": []
    }
    # fetch all artist ids and names
    artists = db.session.query(Artist.id, Artist.name).all()
    # fetch the searching term from form
    s_term = request.form.get('search_term').lower()
    # print searching term to confirm
    # print(s_term)
    if not s_term:
        # error message for blank searching term
        flash("You did not search for anything")
    elif s_term:
        for artist in artists:
            id = artist.id
            name = artist.name  # assign id and name of artist in current loop
            if name.lower().find(s_term) != -1:
                artist = {  # if match with searching term,
                    'id': id,  # add artist id and name to artist dictionary
                    'name': name
                }
                # append matched artist to response dictionary
                response['data'].append(artist)
        # count number of entries in the response dictionary
        response['count'] = len(response['data'])
    # print used to confirm if there is match and response created
    # print(name.find(s_term))
    # print(response)
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    # fetch artist data for matched artist
    artist = Artist.query.filter_by(id=artist_id).first()
    # fetch show data for matched artist
    shows = artist_id

    data = {    # assign artist's details to data dictionary
        "name": artist.name,
        "id": artist.id,
        "genres": ''.join(list(filter(
            lambda x: x != '{' and x != '}',
            artist.genres))).split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.searching_artist,
        "seeking_description": artist.desc,
        "image_link": artist.image_link,
        "upcoming_shows": upcoming_shows_artists(shows),
        "upcoming_shows_count": len(upcoming_shows_artists(shows)),
        "past_shows": past_shows_artists(shows),
        "past_shows_count": len(past_shows_artists(shows))
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    if form.validate():  # run validators on form
        try:
            # fetch data for artist being edited
            artist_data = Artist.query.get(artist_id)
            artist_data.name = form.name.data
            artist_data.city = form.city.data
            artist_data.state = form.state.data
            artist_data.phone = form.phone.data
            artist_data.genres = form.genres.data
            artist_data.facebook_link = form.facebook_link.data
            artist_data.image_link = form.image_link.data
            artist_data.website = form.website_link.data
            artist_data.searching_artist = form.seeking_venue.data
            # replace the existing data with new data
            artist_data.desc = form.seeking_description.data
            artist_submission = db.session.merge(artist_data)
            db.session.add(artist_submission)
            db.session.commit()   # commit changes to DB

        # on successful db insert, flash success
            flash(
                'Artist ' +
                request.form['name'] +
                ' was successfully changed!')  # successful change message

        except BaseException:
            print(sys.exc_info())
            flash(
                'Artist ' +
                request.form['name'] +
                ' could not be changed')   # error message
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)  # invalid form data error message
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm(request.form)
    if form.validate():
        try:
            # fetch data for matched venue id
            venue_data = Venue.query.get(venue_id)
            print(venue_data)
            venue_data.name = form.name.data
            venue_data.city = form.city.data
            venue_data.state = form.state.data
            venue_data.address = form.address.data
            venue_data.phone = form.phone.data
            venue_data.genres = form.genres.data
            venue_data.facebook_link = form.facebook_link.data
            venue_data.image_link = form.image_link.data
            venue_data.website = form.website_link.data
            venue_data.searching_venue = form.seeking_talent.data
            # replace existing data with new data
            venue_data.desc = form.seeking_description.data
            # SQLAlchemy converts to SQL and changes record
            venue_submission = db.session.merge(venue_data)
            db.session.add(venue_submission)
            db.session.commit()    # commit changes to DB

            # Successfull change message
            flash(
                'Venue ' +
                request.form['name'] +
                ' was successfully changed!')
        except BaseException:
            print(sys.exc_info())
            flash(
                'Venue ' +
                request.form['name'] +
                ' could not be changed')  # Error message
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)  # invalid form data

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
    form = ArtistForm()
    # Used to check if validation is working
    # print(form.validate())
    if form.validate():   # run validators for form
        try:
            artist_data = Artist(   # assign form data to artist_data object
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website=form.website_link.data,
                searching_artist=form.seeking_venue.data,
                desc=form.seeking_description.data
            )
            # SQL ALchemy converts to SQL and adds entry
            db.session.add(artist_data)
            db.session.commit()  # commit to DB

        # on successful db insert, flash success
            # successful creation message
            flash(
                'Artist ' +
                request.form['name'] +
                ' was successfully listed!')
        except BaseException:
            print(sys.exc_info())
            flash(
                'Artist ' +
                request.form['name'] +
                ' could not be listed')  # error message
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash(form.errors)  # invalid form data error message
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    shows = Show.query.all()  # get all shows
    data = []
    for show in shows:
        show = {  # assign shows data to show dictionary
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(
                id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "start_time": str(show.start_time)
        }
        data.append(show)  # append each show to data list
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing
    # form
    form = ShowForm()

    if form.validate():  # runs form validators
        try:
            show_data = Show(  # assign form data to show_data
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            # SQLAlchemy converts to SQL and adds record
            db.session.add(show_data)
            db.session.commit()  # commit to DB
            # on successful db insert, flash success
            # Successful creation message
            flash('Show was successfully listed!')
        except BaseException:
            print(sys.exc_info())
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        flash(form.errors)  # invalid form data
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

# function that calculates upcoming shows


def upcoming_shows_artists(shows):
    upcoming = []
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == shows).filter(Show.start_time > datetime.now()).all()
    for show in upcoming_shows_query:
        upcoming.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(
                id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(
                id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(
                id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return upcoming


def upcoming_shows_venues(shows):
    upcoming = []
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == shows).filter(Show.start_time > datetime.now()).all()
    for show in upcoming_shows_query:
        upcoming.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(
                id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(
                id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(
                id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return upcoming

# function that calculates past shows


def past_shows_artists(shows):
    past = []
    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == shows).filter(Show.start_time < datetime.now()).all()
    for show in past_shows_query:
        past.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(
                id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(
                id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(
                id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return past


def past_shows_venues(shows):
    past = []
    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == shows).filter(Show.start_time < datetime.now()).all()
    for show in past_shows_query:
        past.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(
                id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(
                id=show.artist_id).first().image_link,
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(
                id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(
                id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return past


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
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
