import json
import logging
import os
from datetime import datetime

import babel
import dateutil.parser
from flask import Flask, Response, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

from forms import *

app = Flask(__name__)
app.config.from_object("config")

moment = Moment(app)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))

    children = db.relationship("Show", backref="show_venue", cascade="all,delete")


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))

    children = db.relationship("Show", backref="show_artist", cascade="all,delete")


class Show(db.Model):
    __tablename__ = "Shows"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(), nullable=False)

    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)


def get_show_info(show):
    # helper method for show_context
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    return {
        "artist_name": artist.name,
        "artist_id": artist.id,
        "artist_image_link": artist.image_link,
        "venue_name": venue.name,
        "venue_id": venue.id,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time),
    }


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime


@app.route("/")
def index():
    return render_template("pages/home.html")


@app.route("/venues")
def venues():
    areas = Venue.query.distinct("city", "state").all()
    data = []
    for area in areas:
        venues = Venue.query.filter(
            Venue.city == area.city, Venue.state == area.state
        ).all()
        data.append({"city": area.city, "state": area.state, "venues": venues})
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    search_result = Venue.query.filter(Venue.name.ilike(f"%{search_term.lower()}%"))
    response = {
        "count": search_result.count(),
        "data": [{"id": result.id, "name": result.name} for result in search_result],
    }
    return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    shows = Show.query.filter(Show.venue_id == venue_id)
    upcoming_shows = shows.filter(Show.start_time > str(datetime.now())).all()
    upcoming_shows = [get_show_info(show) for show in upcoming_shows]
    past_shows = shows.filter(Show.start_time < str(datetime.now())).all()
    past_shows = [get_show_info(show) for show in past_shows]

    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": set(venue.genres),
        "city": venue.city,
        "address": venue.address,
        "phone": venue.phone,
        "website": venue.website,
        "image_link": venue.image_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "upcoming_shows": upcoming_shows,
        "past_shows": past_shows,
    }
    return render_template("pages/show_venue.html", venue=venue)


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)
    if form.validate_on_submit():
        try:
            venue = Venue()
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()
            flash(f"Succesfully listed {venue.name} (ID: {venue.id})")
            return redirect(url_for("index"))
        except:
            flash(f"Could not list {venue.name} (ID: {venue.id})")
            db.session.rollback()
            return redirect(url_for("create_venue_form"))
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for("index"))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        flash("An error occurred. Artist could not be deleted.")
        app.logger.info("An error occurred. Artist could not be deleted.")
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/artists")
def artists():
    return render_template("pages/artists.html", artists=Artist.query.all())


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    search_result = Artist.query.filter(Artist.name.ilike(f"%{search_term.lower()}%"))
    response = {
        "count": search_result.count(),
        "data": [{"id": result.id, "name": result.name} for result in search_result],
    }
    return render_template(
        "pages/search_artists.html", results=response, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    shows = Show.query.filter(Show.artist_id == artist_id)
    upcoming_shows = shows.filter(Show.start_time > str(datetime.now())).all()
    upcoming_shows = [get_show_info(show) for show in upcoming_shows]
    past_shows = shows.filter(Show.start_time < str(datetime.now())).all()
    past_shows = [get_show_info(show) for show in past_shows]

    artist = Artist.query.get(artist_id)
    artist.genres = set(artist.genres)
    artist.upcoming_shows = upcoming_shows
    artist.past_shows = past_shows
    return render_template("pages/show_artist.html", artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    if form.validate_on_submit():
        try:
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash(f"Succesfully edited {artist.name} (ID: {artist.id})")
            return redirect(url_for("show_artist", artist_id=artist_id))
        except:
            flash(f"Could not edit {artist.name} (ID: {artist.id})")
            db.session.rollback()
            return redirect(url_for("edit_artist", artist_id=artist_id))
        finally:
            db.session.close()
    else:
        flash(f"Could not edit {artist.name} (ID: {artist_id})")
        flash(form.errors)
        return redirect(url_for("edit_artist", artist_id=artist.id))


@app.route("/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
        flash("An error occurred. Artist could not be deleted.")
        app.logger.info("An error occurred. Artist could not be deleted.")
    finally:
        db.session.close()
    return redirect(url_for("index"))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    if form.validate_on_submit():
        try:
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()
            flash(f"Succesfully edited {venue.name} (ID: {venue.id})")
            return redirect(url_for("show_venue", venue_id=venue_id))
        except:
            flash(f"Could not edit {venue.name} (ID: {venue.id})")
            db.session.rollback()
            return redirect(url_for("edit_venue", venue_id=venue_id))
        finally:
            db.session.close()


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        app.logger.info("VALID")
        try:
            artist = Artist()
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            flash(f"Succesfully listed {artist.name} (ID: {artist.id})")
            return redirect(url_for("index"))
        except:
            flash(f"Could not list {artist.name} (ID: {artist.id})")
            db.session.rollback()
            return redirect(url_for("create_artist_form"))
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for("index"))


@app.route("/shows")
def shows():
    shows = Show.query.all()
    shows = [get_show_info(show) for show in shows]
    return render_template("pages/shows.html", shows=shows)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)
    if form.validate_on_submit():
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        artist = Artist.query.get(artist_id)
        venue = Venue.query.get(form.venue_id.data)
        if artist is None:
            flash(f"Invalid artist ID {artist_id}")
        if venue is None:
            flash(f"Invalid venue ID {venue_id}")
        if not (venue and artist):
            flash("retry")
            return redirect(url_for("create_shows"))
        try:
            show = Show()
            form.populate_obj(show)
            db.session.add(show)
            db.session.commit()
            flash(f"Succesfully listed show")
            return redirect(url_for("shows"))
        except:
            flash(f"Could not list show")
            db.session.rollback()
            return redirect(url_for("create_shows"))
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = logging.FileHandler("error.log")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
