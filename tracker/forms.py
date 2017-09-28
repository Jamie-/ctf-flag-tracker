from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

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
    add = SubmitField(label='Add')
    update = SubmitField(label='Update')
    delete = SubmitField(label='Delete')

class AdminFlagForm(FlaskForm):
    flag = StringField('flag', validators=[DataRequired()])
    value = IntegerField('value', validators=[DataRequired()])
    event_id = IntegerField('event_id', validators=[Optional()])
    add = SubmitField(label='Add')
    update = SubmitField(label='Update')
    delete = SubmitField(label='Delete')

class AdminUserForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    admin = BooleanField('admin')
    update = SubmitField(label='Update')

class AdminRankForm(FlaskForm):
    rank = StringField('rank', validators=[DataRequired()])
    score = IntegerField('score', validators=[NumberRange(min=0)])
    add = SubmitField(label='Add')
    update = SubmitField(label='Update')
    delete = SubmitField(label='Delete')
