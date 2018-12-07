import flask
import flask_login
import logging
from tracker import app
import tracker.forms as forms
import tracker.leaderboard as leaderboard
import tracker.auth as auth
import tracker.event as event
import tracker.team as team
import tracker.flag as flag
import tracker.user as user
import tracker.rank as rank

logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return flask.render_template('leaderboard.html', title='Leaderboard', heading='Global Leaderboard', users=leaderboard.get_global())


@app.route('/register', methods=['GET', 'POST'])
def route_register():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already logged in, to register a new user please log out first.', 'warning')
        return flask.redirect('/')
    form = forms.RegisterForm()
    if form.validate_on_submit():
        if user.exists(form.username.data):
            form.username.errors.append('That username is already taken, please pick another one.')
            return flask.render_template('register.html', title='Register', form=form)
        if form.password.data != form.password2.data:
            form.password2.errors.append('Repeat password does not match.')
            return flask.render_template('register.html', title='Register', form=form)
        auth.create_user(form.username.data, form.name.data, form.password.data)
        flask.flash('User account created successfully.', 'success')
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        flask.flash('You are already logged in, to change user please log out first.', 'warning')
        return flask.redirect('/')
    form = forms.LoginForm()
    if form.validate_on_submit():
        u = auth.check_login(form.username.data, form.password.data)
        if u:
            flask_login.login_user(u)
            flask.flash('Welcome back, %s.' % flask.escape(u.display_name), 'success')
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


@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def get_event(event_id):
    e = event.get_event(event_id)
    if e is None:
        flask.abort(404)

    indiv_lb = e.get_leaderboard(limit=6)  # Individual leaderboard
    team_lb = e.get_team_leaderboard(limit=6)  # Team leaderboard

    if flask.request.method == 'POST':
        if not flask_login.current_user.is_authenticated:  # Check user is logged in
            flask.abort(405)
        if e.get_users_team(flask_login.current_user.username) is not None:  # Check user is not already in a team
            flask.abort(405)
        team_form = forms.TeamForm()
        if team_form.validate_on_submit():  # Check form completed properly
            if team_form.create.data:  # Create a team (Create button pressed)
                if team.create_team(team_form.team.data, event_id):  # Team created okay
                    flask.flash('Created team {} successfully!'.format(team_form.team.data), 'success')
                else:  # Unable to create team
                    team_form.team.errors.append('Unable to create team {}, it may already exist in this event.'.format(team_form.team.data))
                    return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form, team_lb=team_lb, indiv_lb=indiv_lb)
            # Add user to team if just created or if Join button pressed
            if e.add_user_to_team(flask_login.current_user.username, team.generate_slug(team_form.team.data)):  # Team joined okay
                flask.flash('Joined team {} successfully!'.format(team_form.team.data), 'success')
                return flask.redirect('/event/' + str(event_id), code=302)
            else:  # Unable to join team
                team_form.team.errors.append('Unable to join team {}, it may not exist in this event.'.format(team_form.team.data))
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form, team_lb=team_lb, indiv_lb=indiv_lb)
        return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=team_form, team_lb=team_lb, indiv_lb=indiv_lb)

    if e.has_teams():
        if flask_login.current_user.is_authenticated:
            t = e.get_users_team(flask_login.current_user.username)
            if t is None:
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, form=forms.TeamForm(), team_lb=team_lb, indiv_lb=indiv_lb)
            else:
                return flask.render_template('event_teams.html', title=e.name, event=e, user=flask_login.current_user, team=t, team_lb=team_lb, indiv_lb=indiv_lb)
        else:
            return flask.render_template('event_teams.html', title=e.name, event=e, team_lb=team_lb, indiv_lb=indiv_lb)
    else:
        title = e.name + ' Leaderboard'
        return flask.render_template('leaderboard.html', title=title, heading=title, users=e.get_leaderboard(), num_flags=e.get_num_flags())


@app.route('/event/<int:event_id>/team')
def event_team(event_id):
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)  # User not logged in so has no team nor can create/join a team
    t = event.get_event(event_id).get_users_team(flask_login.current_user.username)
    if t is None:
        flask.abort(404)
    return flask.redirect('/event/' + str(event_id) + '/team/' + t.get_slug(), code=302)


@app.route('/event/<int:event_id>/teams')
def event_teams(event_id):
    # Redirect to normal event (which shows individual leaderboard) when event has no teams
    if not event.get_event(event_id).has_teams():
        return flask.redirect('/event/' + str(event_id), code=302)

    e = event.get_event(event_id)
    title = e.name + ' Teams Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, teams=e.get_team_leaderboard(), num_flags=e.get_num_flags())


@app.route('/event/<int:event_id>/individual')
def event_individual(event_id):
    # Redirect to normal event (which shows individual leaderboard) when event has no teams
    if not event.get_event(event_id).has_teams():
        return flask.redirect('/event/' + str(event_id), code=302)

    e = event.get_event(event_id)
    title = e.name + ' Individual Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, users=e.get_leaderboard(), num_flags=e.get_num_flags())


@app.route('/event/<int:event_id>/team/<string:team_slug>')
def event_inter_team(event_id, team_slug):
    e = event.get_event(event_id)
    if e is None:
        flask.abort(404)
    t = e.get_team(team_slug)
    if (not e.has_teams()) or t is None:
        flask.abort(404)
    title = t.name + ' Leaderboard'
    return flask.render_template('leaderboard.html', title=title, heading=title, users=t.get_leaderboard())


@app.route('/events')
def get_events():
    return flask.render_template('event_list.html', title='Events', events=event.get_all())


@app.route('/flag', methods=['GET', 'POST'])
@flask_login.login_required
def check_flag():
    form = forms.FlagForm()
    if form.validate_on_submit():
        f = flag.check(form.flag.data, flask_login.current_user.get_id())
        if f:  # Flag is valid and user has not previously found it
            return flask.redirect('/flag/boom', code=307)
        elif f is None:  # User already has flag
            flask.flash("You've already submitted that flag.", 'primary')
        elif not f:  # Not valid flag
            flask.flash("Oh, that's not a valid flag :(", 'warning')
    return flask.render_template('flag.html', title='Submit Flag', form=form)


@app.route('/flag/boom', methods=['GET', 'POST'])
@flask_login.login_required
def flag_success():
    if flask.request.method == 'POST':
        f = flag.get_flag(flask.request.form['flag'])
        if f is not None:
            return flask.render_template('flag_success.html', title='Yay! Flag Added', flag=f, user=flask_login.current_user)
    return flask.redirect('/flag', code=302)


@app.route('/profile')
def profile():
    if flask_login.current_user.is_authenticated:
        return flask.redirect('/profile/' + flask_login.current_user.get_id())
    flask.abort(404)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile_user(username):
    if not user.exists(username):
        flask.abort(404)
    u = user.get_user(username)

    if flask_login.current_user.get_id() == u.username:
        dn_form = forms.ChangeDisplayNameForm(prefix='dn')
        pwd_form = forms.ChangePasswordForm(prefix='pwd')

        if dn_form.submit.data and dn_form.validate_on_submit():
            u.update_display_name(dn_form.display_name.data)
            flask.flash('Display name updated successfully.', 'success')
            dn_form.display_name.data = ''  # Clear input field

        if pwd_form.submit.data and pwd_form.validate_on_submit():
            if auth.check_login(username, pwd_form.old_password.data):
                if pwd_form.new_password.data == pwd_form.new_password2.data:
                    u.update_password(pwd_form.new_password.data)
                    flask.flash('Password updated successfully.', 'success')
                else:
                    pwd_form.new_password2.errors.append('Repeated password does not match.')
            else:
                pwd_form.old_password.errors.append('Old password is incorrect.')

        return flask.render_template('profile_my.html', title=u.display_name, user=u, events=event.by_user(username), rank=rank.get_rank(u.get_global_score()), dn_form=dn_form, pwd_form=pwd_form)

    return flask.render_template('profile.html', title=u.display_name, user=u, events=event.by_user(username), rank=rank.get_rank(u.get_global_score()))


@app.route('/profile/<username>/delete', methods=['GET', 'POST'])
def profile_delete(username):
    u = user.get_user(username)
    if flask_login.current_user.get_id() == u.username:
        form = forms.ConfirmPasswordForm()
        if form.validate_on_submit():
            if auth.check_login(u.username, form.password.data):
                u.remove()  # Must be called before logout to allow event to be logged correctly
                flask_login.logout_user()
                flask.flash('Account deleted.', 'success')
                return flask.redirect('/')
            else:
                form.password.errors.append('Incorrect password.')
        return flask.render_template('delete_account.html', title='Delete Account', user=u, form=form)
    else:
        flask.abort(404)
