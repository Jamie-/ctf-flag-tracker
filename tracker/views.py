import flask
import flask_login
from tracker import app
from tracker.user import User
import tracker.forms as forms
import tracker.leaderboard as leaderboard
import tracker.auth as auth
import tracker.event as event
import tracker.team as team
import tracker.flag as flag
import tracker.user as user

@app.route('/')
def index():
    users = leaderboard.get_data()
    return flask.render_template('leaderboard.html', title='Leaderboard', heading='Global Leaderboard', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        name = auth.check_login(form.username.data, form.password.data)
        if name:
            flask_login.login_user(User(form.username.data, name))
            flask.flash('Welcome back, %s.' % flask.escape(name), 'success')

            return flask.redirect('/')
        else:
            flask.flash('Invalid user credentials, please try again.', 'danger')
    return flask.render_template('login.html', title='Login', form=form)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect('/')

@app.route('/event')
def current_event():
    e = event.get_active()
    if e is not None:
        return flask.redirect('/event/' + str(e.id), code=302)
    return flask.render_template('error.html', title='Current Event', heading=':(', text="We currently aren't running an event right now. Check back later!")

@app.route('/event/<int:event_id>')
def get_event(event_id):
    e = event.get_event(event_id)
    if e is None:
        flask.abort(404)

    indiv_lb = e.get_leaderboard(limit=6)  # Individual leaderboard
    team_lb = e.get_team_leaderboard(limit=6) # Team leaderboard
    if e.has_teams():
        if flask_login.current_user.is_authenticated:
            t = flask_login.current_user.get_team(e.id)
            if t is None:
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=forms.TeamForm(), team_lb=team_lb, indiv_lb=indiv_lb)
            else:
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, team=t, team_lb=team_lb, indiv_lb=indiv_lb)
        else:
            return flask.render_template('event_teams.html', title=e.name, event=e, team_lb=team_lb, indiv_lb=indiv_lb)
    else:
        title = e.name + ' Leaderboard'
        return flask.render_template('leaderboard.html', title=title, heading=title, users=e.get_leaderboard(), no_flags=e.no_flags)

@app.route('/event/<int:event_id>/team', methods=['GET', 'POST'])
def event_team(event_id):
    if not flask_login.current_user.is_authenticated:
        flask.abort(404) # User not logged in so has no team nor can create/join a team

    if flask.request.method == 'POST':
        e = event.get_event(event_id)
        team_form = forms.TeamForm()
        if team_form.validate_on_submit(): # Check form completed properly
            team_data = flask.escape(team_form.team.data)
            if team_form.create.data: # Create a team (Create button pressed)
                if team.create_team(team_data, event_id): # Team created okay
                    flask.flash('Created team %s successfully!' % team_data, 'success')
                else: # Unable to create team
                    team_form.team.errors.append('Unable to create team %s, it may already exist in this event.' % team_data)
                    return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form)
            # Add user to team if just created or if Join button pressed
            t = team.join_team(flask_login.current_user.id, team_data, event_id)
            if t: # Team joined okay
                flask.flash('Joined team %s successfully!' % team_data, 'success')
                return flask.redirect('/event/' + str(event_id), code=302)
            else: # Unable to join team
                team_form.team.errors.append('Unable to join team %s, it may not exist in this event.' % team_data)
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form)
        return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form)
    else: # flask.request.method == 'GET'
        t = flask_login.current_user.get_team(event_id)
        if t is None:
            flask.abort(404)
        return flask.redirect('/event/' + str(event_id) + '/team/' + t.name, code=302)

@app.route('/event/<int:event_id>/teams')
def event_teams(event_id):
    # Redirect to normal event (which shows individual leaderboard) when event has no teams
    if not event.get_event(event_id).has_teams():
        return flask.redirect('/event/' + str(event_id), code=302)

    e = event.get_event(event_id)
    title = e.name + ' Team Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, users=e.get_team_leaderboard(), no_flags=e.no_flags)

@app.route('/event/<int:event_id>/individual')
def event_individual(event_id):
    # Redirect to normal event (which shows individual leaderboard) when event has no teams
    if not event.get_event(event_id).has_teams():
        return flask.redirect('/event/' + str(event_id), code=302)

    e = event.get_event(event_id)
    title = e.name + ' Individual Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, users=e.get_leaderboard(), no_flags=e.no_flags)

@app.route('/event/<int:event_id>/team/<string:team_name>')
def event_inter_team(event_id, team_name):
    e = event.get_event(event_id)
    if e is None:
        flask.abort(404)
    t = e.get_team(team_name)
    if (not e.has_teams()) or t is None:
        flask.abort(404)
    title = team_name + ' Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, users=t.get_leaderboard())

@app.route('/events')
def get_events():
    return flask.render_template('event_list.html', title='Events', events=event.get_all_events())

@app.route('/flag', methods=['GET', 'POST'])
@flask_login.login_required
def check_flag():
    form = forms.FlagForm()
    if form.validate_on_submit():
        f = flag.check(form.flag.data, flask_login.current_user.get_id())
        if f: # Flag is valid and user has not previously found it
            return flask.redirect('/flag/boom', code=307)
        elif f is None: # User already has flag
            flask.flash('You\'ve already submitted that flag.', 'primary')
        elif not f: # Not valid flag
            flask.flash('Oh, that\'s not a valid flag :(', 'warning')
    return flask.render_template('flag.html', title='Submit Flag', form=form)

@app.route('/flag/boom', methods=['GET', 'POST'])
@flask_login.login_required
def flag_success():
    if flask.request.method == 'POST':
        f = flag.get_flag(flask.request.form['flag'])
        return flask.render_template('flag_success.html', title='Yay! Flag Added', flag=f, user=flask_login.current_user)
    else:
        return flask.redirect('/flag', code=302)

@app.route('/profile')
def profile():
    if flask_login.current_user.is_authenticated:
        return flask.redirect('/profile/' + flask_login.current_user.get_id())
    flask.abort(404)

@app.route('/profile/<string:user_id>')
def profile_user(user_id):
    if not user.exists(user_id):
        flask.abort(404)
    u = user.get_user(user_id)
    return flask.render_template('profile.html', title=u.name, user=u, events=u.get_events_attended())


## Error Handlers

@app.errorhandler(400)
def error_400(error):
    return flask.render_template('error.html', title='400', heading='Error 400', text="Oh no, that's an error!")

@app.errorhandler(401)
def error_401(error):
    return flask.render_template('error.html', title='401', heading='Error 401', text="Oh no, that's an error!")

@app.errorhandler(403)
def error_403(error):
    return flask.render_template('error.html', title='403', heading='Error 403', text="Oh no, that's an error!")

@app.errorhandler(404)
def error_404(error):
    return flask.render_template('error.html', title='404', heading='Error 404', text="Oh no, that's an error!")

@app.errorhandler(500)
def error_500(error):
    return flask.render_template('error.html', title='500', heading='Error 500', text="Oh no, that's an error!")
