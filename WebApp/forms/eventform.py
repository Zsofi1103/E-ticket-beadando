from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


from wtforms import Field

class EventForm(FlaskForm):
    title = StringField('Esemény címe', validators=[DataRequired(), Length(min=1, max=255)])
    description = TextAreaField('Leírás', validators=[Optional(), Length(max=1000)])
    category_id = SelectField('Kategória', coerce=int, validators=[Optional()])
    venue_id = SelectField('Helyszín', coerce=int, validators=[Optional()])
    start_at = StringField('Kezdés (dátum és idő)', validators=[Optional()])
    price = DecimalField('Ár (Ft)', places=2, validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Mentés')