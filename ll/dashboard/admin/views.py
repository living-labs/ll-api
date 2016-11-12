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
import os
import pickle
from .. import core, requires_login



mod = Blueprint('admin', __name__, url_prefix='/admin')


@mod.route('/')
@requires_login
def admin():
    if not g.user["is_admin"]:
        flash(u'You need to be admin for this page.', 'alert-warning')
        return redirect("/")
    participants = core.user.get_participants()
    queries = core.query.get_query()
    sites = [s for s in core.site.get_sites()]
    active_participants = set()
    site_participants = {}
    site_queries = {}
    for query in queries:
        if not query["site_id"] in site_participants:
            site_participants[query["site_id"]] = [set(), set()]
        if not query["site_id"] in site_queries:
            site_queries[query["site_id"]] = [0, 0]
        if "runs" in query:
            if "type" in query and query["type"] == "test":
                site_queries[query["site_id"]][1] += 1
            else:
                site_queries[query["site_id"]][0] += 1
            for u in query["runs"]:
                active_participants.add(u)
                if "type" in query and query["type"] == "test":
                    site_participants[query["site_id"]][1].add(u)
                else:
                    site_participants[query["site_id"]][0].add(u)

    stats = {"participants": {"verified":  0,
                              "all":  0,
                              "active":  0
                              },
             "sites": {"runs": 0,
                       "all":  0,
                       "active": 0},
             "queries": 0,
             "per_site": {site["_id"]: {"participants": {"train": 0, "test":0},
                                        "queries": {"train":0, "test":0}
                                    } for site in sites
                          }
             }

    stats_file = "stats_admin.p"
    if os.path.isfile(stats_file):
        stats = pickle.load(open(stats_file,"rb"))

    return render_template("admin/admin.html", user=g.user, stats=stats, config=core.config.config)

@mod.route('/<site_id>/run')
@requires_login
def run(site_id):
    n_runs = 1000
    site = core.site.get_site(site_id)
    runs=core.db.db.run.find({"site_id": site_id})
    sorted_runs = sorted(runs, key=lambda x: x["creation_time"], reverse=True)[:n_runs]
    user_dict = {}
    users = core.user.get_users()
    for user in users:
        user_dict[user["_id"]] = user["teamname"]
    
    return render_template("admin/run.html",
                           user = g.user,
                           site=site,
                           config=core.config.config,
                           runs=sorted_runs,
                           user_dict = user_dict,
                           n = n_runs)
                           

@mod.route('/outcome/<site_id>')
@requires_login
def outcome(site_id):
    if not g.user["is_admin"]:
        flash(u'You need to be admin for this page.', 'alert-warning')
        return redirect("/")
    participants = core.user.get_participants()
    outcomes = []
    for participant in participants:
        if not participant["is_verified"]:
            continue
        outcome_test = core.feedback.get_comparison(userid=participant["_id"],
                                                    site_id=site_id,
                                                    qtype='test')
        outcome_train = core.feedback.get_comparison(userid=participant["_id"],
                                                     site_id=site_id,
                                                     qtype='train')
        outcomes.append((outcome_test, {"outcome": {"test": outcome_test,
                                                    "train": outcome_train[0]},
                                        "user": participant}))
    outcomes = [o for _, o in sorted(outcomes, reverse=True)]
    return render_template("admin/outcome.html", user=g.user,
                           outcomes=outcomes, site_id=site_id, config=core.config.config)
