import flask_wtf
import wtforms
import wtforms.validators as validators


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