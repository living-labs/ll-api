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

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
import json
from .. import core, requires_login

mod = Blueprint('my', __name__, url_prefix='/my')


@mod.route('/')
@requires_login
def my():
    if g.user["is_participant"]:
        sites = [s for s in core.site.get_sites()
                 if g.user["is_admin"] or
                 s["_id"] in core.user.get_sites(g.user["_id"])]
    else:
        sites = core.site.get_sites()
    return render_template("my/my.html", user=g.user, sites=sites,config=core.config.config)


@mod.route('/<site_id>')
@requires_login
def site(site_id):
    site = core.site.get_site(site_id)
    feedbacks = core.db.db.feedback.find({"site_id": site_id,
                                          "userid": g.user["_id"]})
    clicks = 0
    for feedback in feedbacks:
        if "doclist" not in feedback:
            continue
        clicks += len([d for d in feedback["doclist"]
                       if "clicked" in d and d["clicked"]])

    stats = {"run": core.db.db.run.find({"site_id": site_id,
                                         "userid": g.user["_id"]}).count(),
             "query": core.db.db.query.find({"site_id": site_id}).count(),
             "doc": core.db.db.doc.find({"site_id": site_id}).count(),
             "impression": feedbacks.count(),
             "click": clicks,
             }

    return render_template("my/site.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           stats=stats)
