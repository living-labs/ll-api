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


import os
import rollbar
import rollbar.contrib.flask
from functools import wraps
from flask import Flask, render_template, g, flash, redirect, url_for,\
    request, session, got_request_exception
from .. import core
app = Flask(__name__)


@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    if app.debug:
        return
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        core.config.config["ROLLBAR_DASHB0ARD_KEY"],
        # environment name
        core.config.config["ROLLBAR_ENV"],
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', user=g.user, config=core.config.config), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', user=g.user,config=core.config.config), 500


@app.before_request
def before_request():
    """
    pull user's profile from the database before every request are treated
    """
    g.user = None
    if 'key' in session:
        g.user = core.user.get_user(session['key'])


@app.route('/')
def home():
    return render_template("base.html", user=g.user,
                           sites=core.user.get_sites(g.user["_id"])
                           if g.user else True,
                           verified=g.user["is_verified"]
                           if g.user else True,
                           config=core.config.config)


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash(u'You need to be signed in for this page.', 'alert-warning')
            return redirect(url_for('user.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

from user.views import mod as userModule
app.register_blueprint(userModule)
from site.views import mod as siteModule
app.register_blueprint(siteModule)
from participant.views import mod as participantModule
app.register_blueprint(participantModule)
from my.views import mod as myModule
app.register_blueprint(myModule)
from admin.views import mod as adminModule
app.register_blueprint(adminModule)

