import flask
import flask_login
import logging
from tracker import app
import tracker.forms_admin as forms
import tracker.event as event
import tracker.flag as flag
import tracker.user as user
import tracker.rank as rank

logger = logging.getLogger(__name__)


@app.route('/admin')
def admin():
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)
    return flask.redirect('/admin/events', code=302)


@app.route('/admin/events', methods=['GET', 'POST'])
def admin_events():
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)

    form = forms.AdminEventForm()
    if form.validate_on_submit():
        teams = 0
        active = 0
        if form.teams.data:
            teams = 1
        if form.active.data:
            active = 1

        if form.add.data:  # Add event
            if event.exists(form.id.data):
                flask.flash('An event already exists with that ID, try a different ID.', 'danger')
            else:
                event.create(form.id.data, form.name.data, teams, active)
                flask.flash('Event added successfully!', 'success')
                logger.info("'%s' added an event - %d:'%s'.", flask_login.current_user.username, form.id.data, form.name.data)
        elif form.update.data:  # Update event
            if event.exists(form.id.data):
                event.update(form.id.data, form.name.data, teams, active)
                logger.info("'%s' updated the %d:'%s' event.", flask_login.current_user.username, form.id.data, form.name.data)
            else:
                flask.flash("That event does not exist so can't be updated!", 'danger')
        elif form.delete.data:  # Delete event
            if event.exists(form.id.data):
                event.delete(form.id.data)
                flask.flash('Event deleted successfully.', 'success')
                logger.info("'%s' deleted the %d:'%s' event.", flask_login.current_user.username, form.id.data, form.name.data)
            else:
                flask.flash('Unable to delete event as it does not exist.', 'danger')
    return flask.render_template('admin/events.html', title='Events - Admin', events=event.get_all(), form=form)


@app.route('/admin/flags', methods=['GET', 'POST'])
def admin_flags():
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)

    form = forms.AdminFlagForm()
    if form.validate_on_submit():
        if form.add.data:  # Add flag
            if flag.exists(form.flag.data):
                flask.flash('Unable to add flag, it already exists.', 'danger')
            elif (form.event_id.data is not None) and not (event.exists(form.event_id.data)):
                flask.flash('Unable to add flag, that event ID does not exist.', 'danger')
            else:
                flag.add(form.flag.data, form.value.data, form.event_id.data, form.notes.data)
                flask.flash('Added flag successfully.', 'success')
                logger.info("^%s^ added the flag '%s'.", flask_login.current_user.username, form.flag.data)
        elif form.update.data:  # Update flag
            if flag.exists(form.flag.data):
                if (form.event_id.data is None) or (event.exists(form.event_id.data)):
                    flag.update(form.flag.data, form.value.data, form.event_id.data, form.notes.data)
                    flask.flash('Flag updated successfully.', 'success')
                    logger.info("^%s^ updated the flag '%s'.", flask_login.current_user.username, form.flag.data)
                else:
                    flask.flash('Unable to update flag, that event ID does not exist.', 'danger')
            else:
                flask.flash('Unable to update flag as it does not exist.', 'danger')
        elif form.delete.data:  # Delete flag
            if flag.exists(form.flag.data):
                flag.delete(form.flag.data)
                flask.flash('Flag deleted successfully.', 'success')
                logger.info("^%s^ deleted the flag '%s'.", flask_login.current_user.username, form.flag.data)
            else:
                flask.flash('Unable to delete flag as it does not exist.', 'danger')
    return flask.render_template('admin/flags.html', title='Flags - Admin', flags=flag.get_all(), form=form)


@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)

    if flask.request.method == 'POST' and 'username' in flask.request.form and 'admin' in flask.request.form:
        username = flask.request.form['username']
        admin = False
        if flask.request.form['admin'] == 'true':  # Handle weird jQuery POST
            admin = True

        if user.exists(username):
            user.get_user(username).set_admin(admin)
            if admin:
                logger.info('^%s^ granted admin privileges to ^%s^.', flask_login.current_user.username, username)
            else:
                logger.info('^%s^ revoked admin privileges from ^%s^.', flask_login.current_user.username, username)
            flask.flash('User updated successfully.', 'success')
        else:
            flask.flash('Unable to update user privileges, that username does not exist.', 'danger')
    return flask.render_template('admin/users.html', title='Users - Admin', users=user.get_all(sort_asc=True, admin_first=True))


@app.route('/admin/ranks', methods=['GET', 'POST'])
def admin_ranks():
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)

    form = forms.AdminRankForm()
    if form.validate_on_submit():
        if form.add.data:  # Add rank
            if rank.exists(form.rank.data):
                flask.flash('Unable to add that rank, it already exists.', 'danger')
            else:
                rank.add(form.rank.data, form.score.data)
                flask.flash('Rank added successfully.', 'success')
                logger.info("^%s^ added the rank '%s'.", flask_login.current_user.username, form.rank.data)
        elif form.update.data:  # Update rank
            if rank.exists(form.rank.data):
                rank.update(form.rank.data, form.score.data)
                flask.flash('Rank updated successfully.', 'success')
                logger.info("^%s^ updated the rank '%s'.", flask_login.current_user.username, form.rank.data)
            else:
                flask.flash("Unable to update that rank, it doesn't exist.", 'danger')
        elif form.delete.data:  # Delete rank
            if rank.exists(form.rank.data):
                rank.delete(form.rank.data)
                flask.flash('Rank deleted successfully.', 'success')
                logger.info("^%s^ deleted the rank '%s'.", flask_login.current_user.username, form.rank.data)
            else:
                flask.flash("Unable to delete that rank, it doesn't exist.", 'danger')
    return flask.render_template('admin/ranks.html', title='Ranks - Admin', ranks=rank.get_all(), form=form)


@app.route('/admin/user/<string:user_id>')
def admin_user(user_id):
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)

    u = user.get_user(user_id)
    if u is not None:
        return flask.render_template('admin/user.html', title=user_id+' - Admin', user=u)
    flask.abort(404)


@app.route('/admin/user/<string:user_id>/remove', methods=['POST'])
def remove_user(user_id):
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)
    if 'remove' not in flask.request.form:
        flask.abort(400)

    if user_id == flask_login.current_user.get_id():
        flask.flash("You can't delete your own user here, you need to go to your profile page.", 'danger')
    else:
        u = user.get_user(user_id)
        u.remove()
        flask.flash('User removed.', 'success')
        logger.info('^%s^ deleted the user ^%s^.', flask_login.current_user.get_id(), user_id)

    return flask.redirect('/admin/users')


@app.route('/admin/user/<string:user_id>/removeflag', methods=['POST'])
def remove_flag(user_id):
    if not flask_login.current_user.is_authenticated:
        flask.abort(404)
    elif not flask_login.current_user.is_admin():
        flask.abort(404)
    if 'flag' not in flask.request.form:
        flask.abort(400)

    flag.remove_flag(flask.request.form['flag'], user_id)
    flask.flash('Flag removed.', 'success')

    return flask.redirect("/admin/user/{}".format(user_id))
