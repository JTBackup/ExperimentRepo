from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectMultipleField 
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import DataRequired
from .constants import SOCIAL_MEDIA_PLATFORMS


class DemoForm(FlaskForm):
    first_name = StringField('First Name: ', [DataRequired()])
    last_name = StringField('Last Name: ', [DataRequired()])
    age = StringField('Age: ', [DataRequired()])
    email = StringField('Email: ', [DataRequired()])
    gender = RadioField('Gender: ', [DataRequired()], choices=['Male', 'Female', 'Other'])
    type_of_participant = RadioField('Type of Participant', [DataRequired()],
                                     choices=['Introductory to Psychology Student at The University of Toronto St. George Campus',
                                              'Introductory to Psychology Student at The University of Toronto Scarborough Campus',
                                              "Other (Anyone who doesn't belong to the three previous categories)"])
    time_spent = StringField('Total Time Spent on Social Media: ', [DataRequired()])
    platforms_used = SelectMultipleField('Social Media Platforms Used',
                                         choices=[(platform, platform) for platform in SOCIAL_MEDIA_PLATFORMS],
                                         widget=ListWidget(prefix_label=False),
                                         option_widget=CheckboxInput())
    submit = SubmitField('Submit')
