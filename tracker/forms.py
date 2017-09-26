from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class FlagForm(FlaskForm):
    flag = StringField('flag', validators=[DataRequired()])

class TeamForm(FlaskForm):
    team = StringField('team',validators=[DataRequired(), Length(3)])
    create = SubmitField(label='Create')
    join = SubmitField(label='Join')


# Admin Forms
class AdminEventForm(FlaskForm):
    id = IntegerField('id', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    teams = BooleanField('teams')
    active = BooleanField('active')
