import flask
import flask_login
from tracker import app
from tracker.forms import FlagForm, LoginForm
from tracker.user import User
import tracker.auth as auth
import tracker.flag as flag

@app.route('/')
def index():

    return flask.render_template('leaderboard.html', title='Leaderboard')

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
        if flag.check(form.flag.data, None):
            return flask.redirect('/flag/boom', code=307)
        else:
            flask.flash('Oh, that\'s not a valid flag :(', 'warning')
    return flask.render_template('flag.html', title='Submit Flag', form=form)

@app.route('/flag/boom', methods=['GET', 'POST'])
@flask_login.login_required
def flag_success():
    if flask.request.method == 'POST':
        return flask.render_template('flag_success.html', title='Yay! Flag Added', flag=flask.request.form['flag'])
    else:
        return flask.redirect('/flag', code=302)

@app.route('/profile/<string:user_id>')
def profile(user_id):
    if flask_login.current_user.is_authenticated and flask_login.current_user.get_id() == user_id:
        return flask.render_template('profile.html', title=user_id, user='This is your profile', text=flask_login.current_user.get_name())
    else:
        return flask.render_template('profile.html', title=user_id, user=user_id, text='I am a user!')
