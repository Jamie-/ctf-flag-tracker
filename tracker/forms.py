import flask_wtf
import wtforms
import wtforms.validators as validators
import tracker


class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('username', validators=[validators.DataRequired()])
    password = wtforms.PasswordField('password', validators=[validators.DataRequired()])


class RegisterForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('username', validators=[validators.DataRequired(), validators.Length(min=2, max=32), validators.Regexp('^(?:[a-zA-Z]|\d|-|_|\.)+$', message='Username contains invalid characters.')])
    name = wtforms.StringField('name', validators=[validators.DataRequired(), validators.Length(min=3, max=50)])
    password = wtforms.PasswordField('password', validators=[validators.DataRequired(), validators.Length(min=8)])
    password2 = wtforms.PasswordField('password2', validators=[validators.DataRequired(), validators.Length(min=8)])
    if 'DEBUG' in tracker.app.config and not tracker.app.config['DEBUG']:
        recaptcha = flask_wtf.RecaptchaField()
    else:
        recaptcha = wtforms.HiddenField('nothing')


class FlagForm(flask_wtf.FlaskForm):
    flag = wtforms.StringField('flag', validators=[validators.DataRequired()])


class TeamForm(flask_wtf.FlaskForm):
    team = wtforms.StringField('team', validators=[validators.DataRequired(), validators.Length(3)])
    create = wtforms.SubmitField(label='Create')
    join = wtforms.SubmitField(label='Join')


# Admin Forms
class AdminEventForm(flask_wtf.FlaskForm):
    id = wtforms.IntegerField('id', validators=[validators.DataRequired()])
    name = wtforms.StringField('name', validators=[validators.DataRequired()])
    teams = wtforms.BooleanField('teams')
    active = wtforms.BooleanField('active')
    add = wtforms.SubmitField(label='Add')
    update = wtforms.SubmitField(label='Update')
    delete = wtforms.SubmitField(label='Delete')


class AdminFlagForm(flask_wtf.FlaskForm):
    flag = wtforms.StringField('flag', validators=[validators.DataRequired()])
    value = wtforms.IntegerField('value', validators=[validators.NumberRange(min=0, max=50)])
    event_id = wtforms.IntegerField('event_id', validators=[validators.Optional()])
    notes = wtforms.StringField('notes', widget=wtforms.widgets.TextArea())
    add = wtforms.SubmitField(label='Add')
    update = wtforms.SubmitField(label='Update')
    delete = wtforms.SubmitField(label='Delete')


class AdminRankForm(flask_wtf.FlaskForm):
    rank = wtforms.StringField('rank', validators=[validators.DataRequired()])
    score = wtforms.IntegerField('score', validators=[validators.NumberRange(min=0)])
    add = wtforms.SubmitField(label='Add')
    update = wtforms.SubmitField(label='Update')
    delete = wtforms.SubmitField(label='Delete')
