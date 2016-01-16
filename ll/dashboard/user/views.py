# This file is part of Living Labs Challenge, see http://living-labs.net.
#
# Living Labs Challenge is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Living Labs Challenge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Living Labs Challenge. If not, see <http://www.gnu.org/licenses/>.

from flask.ext.wtf import Form
from wtforms import BooleanField
from flask import Blueprint, request, render_template, flash, g, session, \
                    redirect, url_for
from werkzeug import check_password_hash

from .. import core, requires_login
from forms import LoginForm, RegisterForm, ForgotForm
from bson import json_util
import json
mod = Blueprint('user', __name__, url_prefix='/user')


@mod.route('/me/')
@requires_login
def home():
    return render_template("user/profile.html", user=g.user,
                           config=core.config.config)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Login form
    """
    form = LoginForm(request.form)
    # make sure data are valid, but doesn't validate password is right
    if form.validate_on_submit():
        try:
            user = core.user.get_user_by_email(form.email.data)
        except:
            user = None
        # we use werzeug to validate user's password
        if user and check_password_hash(user["password"], form.password.data):
            # the session can't be modified as it's signed,
            # it's a safe place to store the user id
            session['key'] = user["_id"]
            flash('Logged in %s' % user["teamname"], 'alert-success')
            return redirect(url_for('home'))
        flash('Wrong email or password', 'alert-warning')
    return render_template("user/login.html", form=form, user=g.user, config=core.config.config)


@mod.route('/logout/', methods=['GET'])
def logout():
    """
    Logout
    """
    g.user = None
    del session['key']
    return redirect("/")


@mod.route('/register/', methods=['GET', 'POST'])
def register():
    """
    Registration Form
    """
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        try:
            user = core.user.new_user(form.teamname.data, form.email.data,
                                      password=form.password.data)
        except Exception, e:
            flash(str(e), 'alert-warning')
            return render_template("user/register.html", form=form,
                                   user=g.user, config=core.config.config)
        key = user["_id"]
        session['key'] = key
        flash('Thanks for registering. Your key is: %s' % key, 'alert-success')
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('user.home'))
    return render_template("user/register.html", form=form, user=g.user, config=core.config.config)


@mod.route('/runs/', methods=['GET', 'POST'])
@requires_login
def runs():
    if not g.user["is_participant"]:
        flash('Only participants can select runs. Please register or sign in as a participant', 'alert-warning')
        return redirect(url_for('user.home'))
    if not g.user["is_verified"]:
        flash('You need to be verified first, please send the organizers a signed <a href="%s">registration form<a/>.'
              % core.config.config["URL_REGISTRATION_FORM"], 'alert-warning')
        return redirect(url_for('user.home'))

    class RunsForm(Form):
        pass

    field_to_run = {}

    for run in core.run.get_outdated_runs(g.user["_id"]):
        print "original run"
        print run
        default = False
        creation_time = run['creation_time']
        run_str = json.dumps(run, default=json_util.default)
        field_id = str(run["_id"])
        setattr(RunsForm, field_id, BooleanField(creation_time, description=run_str))
        field_to_run[field_id] = run
    form = RunsForm(request.form)
    if form.validate_on_submit():
        print "form data:"
        print form.data
        selected_runs = [field_to_run[k] for k in form.data if form.data[k]]
        print "following runs will be activated:"
        print selected_runs
        core.run.reactivate_runs(selected_runs)
        flash('Outdated runs have been reactivated.', 'alert-success')
        return redirect(url_for('user.home'))
    return render_template("user/runs.html", form=form, user=g.user, config=core.config.config)

@mod.route('/sites/', methods=['GET', 'POST'])
@requires_login
def sites():
    if not g.user["is_participant"]:
        flash('Only participants can select sites. Please register or sign in as a participant', 'alert-warning')
        return redirect(url_for('user.home'))
    if not g.user["is_verified"]:
        flash('You need to be verified first, please send the organizers a signed <a href="%s">registration form<a/>.'
              % core.config.config["URL_REGISTRATION_FORM"], 'alert-warning')
        return redirect(url_for('user.home'))

    class SitesForm(Form):
        pass

    usersites = core.user.get_sites(g.user["_id"])
    for site in core.site.get_sites():
        if "enabled" in site and not site["enabled"]:
            continue
        description = site["terms"] if "terms" in site and site["terms"] else "No additional terms."
        default = True if site['_id'] in usersites else False
        setattr(SitesForm, site['_id'], BooleanField(site['name'] + ("<img src=\"/static/icon_robot.svg\" style=\"height: 14px; position: relative;top: -3px;left: 2px;\"/>"
                                                                     if site["is_robot"] else ""),
                                                     description=description,
                                                     default=default))

    form = SitesForm(request.form)
    if form.validate_on_submit():
        sites = [k for k in form.data if form.data[k]]
        core.user.set_sites(g.user["_id"], sites)
        flash('Agreements to site terms have been saved.', 'alert-success')
        return redirect(url_for('site.home'))
    return render_template("user/sites.html", form=form, user=g.user, config=core.config.config)

@mod.route('/forgot/', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm(request.form)
    if form.validate_on_submit():
        try:
            core.user.reset_password(form.email.data)
        except Exception, e:
            flash(str(e), 'alert-warning')
            return redirect(url_for('user.forgot'))
        flash('A new password has been sent to %s.' % form.email.data,
              'alert-success')
        return redirect("/")
    return render_template("user/forgot.html", form=form, user=g.user, config=core.config.config)
