import flask_wtf
import wtforms
import wtforms.validators as validators


# Convert string to int unless string is '' in which case we want None
def special_int(string):
    if string == '':
        return None
    else:
        return int(string)


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
    event_id = wtforms.SelectField('event_id', choices=('', 'None'), coerce=special_int, validators=[validators.Optional()])
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
