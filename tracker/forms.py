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


class ChangeDisplayNameForm(flask_wtf.FlaskForm):
    display_name = wtforms.StringField('display_name', validators=[validators.DataRequired(), validators.Length(min=3, max=50)])
    submit = wtforms.SubmitField(label='Update')


class ChangePasswordForm(flask_wtf.FlaskForm):
    old_password = wtforms.PasswordField('old_password', validators=[validators.DataRequired()])
    new_password = wtforms.PasswordField('new_password', validators=[validators.DataRequired(), validators.Length(min=8)])
    new_password2 = wtforms.PasswordField('new_password2', validators=[validators.DataRequired()])
    submit = wtforms.SubmitField(label='Update')


class ConfirmPasswordForm(flask_wtf.FlaskForm):
    password = wtforms.PasswordField('password', validators=[validators.DataRequired()])
