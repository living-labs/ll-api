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

    stats = {"participants": {"verified":  len([u for u in participants
                                                if u["is_verified"]]),
                              "all":  len(participants),
                              "active":  len(active_participants)
                              },
             "sites": {"runs": len(site_participants),
                       "all": len(sites),
                       "active": len([s for s in sites if s["enabled"]])},
             "queries": len(queries),
             "per_site": {site["_id"]: {"participants": {"train": len(site_participants[site["_id"]][0]), "test":len(site_participants[site["_id"]][1])} if site["_id"] in site_participants else {"train":0, "test":0},
                                        "queries": {"train": site_queries[site["_id"]][0], "test":site_queries[site["_id"]][1]} if site["_id"] in site_queries else {"train":0, "test":0}
                                    } for site in sites
                          }
             }
    return render_template("admin/admin.html", user=g.user, stats=stats, config=core.config.config)


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
