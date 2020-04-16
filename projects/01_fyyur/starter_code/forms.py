from datetime import datetime

from data import genres, states
from flask_wtf import Form
from wtforms import (
    DateTimeField,
    SelectField,
    SelectMultipleField,
    StringField,
    ValidationError,
)
from wtforms.validators import URL, AnyOf, DataRequired


def validate_link(form, field):
    link = field.data
    if field.data != "":
        url_check = URL()
        url_check(form, field)


class IsFuture:
    def __call__(self, form, field):
        if field.data < datetime.today():
            raise ValidationError("Future has to be in the future")


class ShowForm(Form):
    artist_id = StringField("artist_id", validators=[DataRequired()])
    venue_id = StringField("venue_id", validators=[DataRequired()])
    start_time = DateTimeField(
        "start_time", validators=[DataRequired(), IsFuture()], default=datetime.today()
    )


class GeneralForm(Form):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField("state", validators=[DataRequired()], choices=states)
    phone = StringField("phone", validators=[DataRequired()])
    image_link = StringField("image_link", validators=[validate_link])
    genres = SelectMultipleField(
        "genres", choices=[("Placeholder", "Select genres")] + genres
    )

    facebook_link = StringField("facebook_link", validators=[validate_link])

    def validate_genres(form, field):
        acceptable = [g[0] for g in genres]
        for d in field.data:
            if d not in acceptable:
                raise ValidationError("Select genres from the form list")


class VenueForm(GeneralForm):
    address = StringField("address", validators=[DataRequired()])


class ArtistForm(GeneralForm):
    pass
