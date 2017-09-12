import flask
import flask_login
from tracker import app
from tracker.forms import FlagForm, LoginForm
from tracker.user import User
import tracker.leaderboard as leaderboard
import tracker.auth as auth
import tracker.flag as flag

@app.route('/')
def index():
    users = leaderboard.get_data()
    return flask.render_template('leaderboard.html', title='Leaderboard', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = auth.check_login(form.username.data, form.password.data)
        if name:
            flask_login.login_user(User(form.username.data, name))
            flask.flash('Welcome back, %s.' % name, 'success')

            return flask.redirect('/')
        else:
            flask.flash('Invalid user credentials, please try again.', 'danger')
    return flask.render_template('login.html', title='Login', form=form)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect('/')

@app.route('/flag', methods=['GET', 'POST'])
@flask_login.login_required
def check_flag():
    form = FlagForm()
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

@app.route('/profile/<string:user_id>')
def profile(user_id):
    if flask_login.current_user.is_authenticated and flask_login.current_user.get_id() == user_id:
        return flask.render_template('profile.html', title=user_id, user='This is your profile', text=flask_login.current_user.get_name())
    else:
        return flask.render_template('profile.html', title=user_id, user=user_id, text='I am a user!')


## Error Handlers

@app.errorhandler(400)
def error_400(error):
    return flask.render_template('error.html', title='400', heading='Error 400')

@app.errorhandler(401)
def error_401(error):
    return flask.render_template('error.html', title='401', heading='Error 401')

@app.errorhandler(403)
def error_403(error):
    return flask.render_template('error.html', title='403', heading='Error 403')

@app.errorhandler(404)
def error_404(error):
    return flask.render_template('error.html', title='404', heading='Error 404')

@app.errorhandler(500)
def error_500(error):
    return flask.render_template('error.html', title='500', heading='Error 500')
