import flask
import flask_login
import logging
import functools
from tracker import app
import tracker.forms_admin as forms
import tracker.event as event
import tracker.flag as flag
import tracker.user as user
import tracker.rank as rank

logger = logging.getLogger(__name__)


# Use as decorator to views that must have admin permissions to be accessed
def admin_required(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if not flask_login.current_user.is_authenticated:
            flask.abort(404)
        elif not flask_login.current_user.is_admin():
            flask.abort(404)
        return func(*args, **kwargs)
    return decorated_function


@app.route('/admin')
@admin_required
def admin():
    return flask.redirect('/admin/events', code=302)


@app.route('/admin/events', methods=['GET', 'POST'])
@admin_required
def admin_events():
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
                flask.flash('Event added successfully.', 'success')
        elif form.update.data:  # Update event
            if event.exists(form.id.data):
                event.update(form.id.data, form.name.data, teams, active)
                flask.flash('Event updated successfully.', 'success')
            else:
                flask.flash("That event does not exist so can't be updated!", 'danger')
        elif form.delete.data:  # Delete event
            if event.exists(form.id.data):
                event.delete(form.id.data)
                flask.flash('Event deleted successfully.', 'success')
            else:
                flask.flash('Unable to delete event as it does not exist.', 'danger')
    return flask.render_template('admin/events.html', title='Events - Admin', events=event.get_all(), form=form)


@app.route('/admin/flags', methods=['GET', 'POST'])
@admin_required
def admin_flags():
    form = forms.AdminFlagForm()
    form.event_id.choices = [('', 'None')] + [(e.id, e.name) for e in event.get_all()]
    if form.validate_on_submit():
        if form.add.data:  # Add flag
            if flag.exists(form.flag.data):
                flask.flash('Unable to add flag, it already exists.', 'danger')
            elif (form.event_id.data is not None) and not (event.exists(form.event_id.data)):
                flask.flash('Unable to add flag, that event ID does not exist.', 'danger')
            else:
                flag.add(form.flag.data, form.value.data, form.event_id.data, form.notes.data)
                flask.flash('Added flag successfully.', 'success')
        elif form.update.data:  # Update flag
            if flag.exists(form.flag.data):
                if (form.event_id.data is None) or (event.exists(form.event_id.data)):
                    flag.update(form.flag.data, form.value.data, form.event_id.data, form.notes.data)
                    flask.flash('Flag updated successfully.', 'success')
                else:
                    flask.flash('Unable to update flag, that event ID does not exist.', 'danger')
            else:
                flask.flash('Unable to update flag as it does not exist.', 'danger')
        elif form.delete.data:  # Delete flag
            if flag.exists(form.flag.data):
                flag.delete(form.flag.data)
                flask.flash('Flag deleted successfully.', 'success')
            else:
                flask.flash('Unable to delete flag as it does not exist.', 'danger')
    return flask.render_template('admin/flags.html', title='Flags - Admin', flags=flag.get_all(), form=form)


@app.route('/admin/flags/bulk', methods=['GET', 'POST'])
@admin_required
def admin_flags_bulk():
    # Check bulk-add line is valid and return parsed data
    def check_line(line):
        # Check we have all the data
        if line.count(',') < 3:
            raise ValueError('Line is missing a comma.')
        parts = line.split(',')
        # Check flag value
        try:
            value = int(parts[1])
            if value < 0 or value > 50:
                raise ValueError()
        except ValueError:
            raise ValueError('Flag value must be an integer between 0 and 50.')
        # Check event ID
        if parts[2] == '':  # Handle flags not tied to an event
            event_id = None
        else:
            try:
                event_id = int(parts[2])
                if event.get_event(event_id) == None:
                    raise ValueError()
            except ValueError:
                raise ValueError('Event must correspond to an existing event ID.')
        return parts[0], value, event_id, ''.join(parts[3:]).strip()

    form = forms.AdminFlagBulkForm()
    if form.validate_on_submit():
        lines = form.flags.data.splitlines()
        data = []
        # Check list submitted
        try:
            for l in lines:
                data.append(check_line(l))

            # Add all flags
            logger.info('^%s^ started a flag bulk add.', flask_login.current_user.get_id())
            flag_count = 0
            for e in data:
                if not flag.exists(e[0]):
                    flag.add(e[0], e[1], e[2], e[3])
                    flag_count += 1
                else:
                    flask.flash("Skipped flag '{}' as it already exists.".format(e[0]), 'warning')
            logger.info('^%s^ bulk add complete, added %d flags.', flask_login.current_user.get_id(), flag_count)
            if flag_count > 0:
                flask.flash('Added {} flags successfully.'.format(flag_count), 'success')
        except ValueError as e:
            form.flags.errors.append(str(e))

    return flask.render_template('admin/flag_bulk.html', title='Bulk Add Flags - Admin', form=form)


@app.route('/admin/flag/<string:flag_hash>')
@admin_required
def admin_flag(flag_hash):
    f = flag.get_by_hash(flag_hash)
    return flask.render_template('admin/flag_users.html', title='Flag Info - Admin', flag=f)  # TODO add delete button functionality


@app.route('/admin/flag/<string:flag_hash>/removeuser', methods=['POST'])
@admin_required
def admin_remove_flag_user(flag_hash):
    if 'user' not in flask.request.form:
        flask.abort(400)

    f = flag.get_by_hash(flag_hash)
    u = user.get_user(flask.request.form['user'])
    if u is not None and f is not None:
        flag.remove_flag(f.flag, u.username)
        flask.flash('Removed flag from user successfully.', 'success')

    return flask.redirect('/admin/flag/{}'.format(flag_hash))


@app.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def admin_users():

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
@admin_required
def admin_ranks():
    form = forms.AdminRankForm()
    if form.validate_on_submit():
        if form.add.data:  # Add rank
            if rank.exists(form.rank.data):
                flask.flash('Unable to add that rank, it already exists.', 'danger')
            else:
                rank.add(form.rank.data, form.score.data)
                flask.flash('Rank added successfully.', 'success')
        elif form.update.data:  # Update rank
            if rank.exists(form.rank.data):
                rank.update(form.rank.data, form.score.data)
                flask.flash('Rank updated successfully.', 'success')
            else:
                flask.flash("Unable to update that rank, it doesn't exist.", 'danger')
        elif form.delete.data:  # Delete rank
            if rank.exists(form.rank.data):
                rank.delete(form.rank.data)
                flask.flash('Rank deleted successfully.', 'success')
            else:
                flask.flash("Unable to delete that rank, it doesn't exist.", 'danger')
    return flask.render_template('admin/ranks.html', title='Ranks - Admin', ranks=rank.get_all(), form=form)


@app.route('/admin/user/<string:user_id>')
@admin_required
def admin_user(user_id):
    u = user.get_user(user_id)
    if u is not None:
        return flask.render_template('admin/user.html', title=user_id+' - Admin', user=u)
    flask.abort(404)


@app.route('/admin/user/<string:user_id>/remove', methods=['POST'])
@admin_required
def remove_user(user_id):
    if 'remove' not in flask.request.form:
        flask.abort(400)

    if user_id == flask_login.current_user.get_id():
        flask.flash("You can't delete your own user here, you need to go to your profile page.", 'danger')
    else:
        u = user.get_user(user_id)
        u.remove()
        flask.flash('User removed.', 'success')

    return flask.redirect('/admin/users')


@app.route('/admin/user/<string:user_id>/removeflag', methods=['POST'])
@admin_required
def remove_flag(user_id):
    if 'flag' not in flask.request.form:
        flask.abort(400)

    flag.remove_flag(flask.request.form['flag'], user_id)
    flask.flash('Flag removed.', 'success')

    return flask.redirect("/admin/user/{}".format(user_id))
