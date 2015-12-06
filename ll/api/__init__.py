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
import time
import rollbar
import rollbar.contrib.flask
from flask import Flask, g, redirect
from flask.ext.restful import Api, abort
from flask_limiter import Limiter
from flask import got_request_exception

from .. import core
from apiutils import ApiResource, ContentField

app = Flask(__name__)
api = Api(app, catch_all_404s=True)

@app.before_first_request
def limit_request():
    if app.debug:
        return
    Limiter(app, global_limits=["300/minute", "10/second"],
            headers_enabled=True)

@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    if app.debug:
        return
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        core.config.config["ROLLBAR_API_KEY"],
        # environment name
        core.config.config["ROLLBAR_ENV"],
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    try:
        diff = int((time.time() - g.start) * 1000)
        response.headers.add('X-Execution-Time', str(diff))
    except:
        pass
    return response

@app.route("/")
def hello():
    return redirect(core.config.config["URL_DOC"])