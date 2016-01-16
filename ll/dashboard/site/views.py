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

mod = Blueprint('site', __name__, url_prefix='/site')


@mod.route('/')
@requires_login
def home():
    if g.user["is_participant"]:
        sites = [s for s in core.site.get_sites()
                 if g.user["is_admin"] or
                 s["_id"] in core.user.get_sites(g.user["_id"])]
    else:
        sites = core.site.get_sites()
    return render_template("site/sites.html", user=g.user, sites=sites, config=core.config.config)


@mod.route('/<site_id>')
@requires_login
def site(site_id):
    site = core.site.get_site(site_id)
    feedbacks = core.db.db.feedback.find({"site_id": site_id})
    clicks = 0
    #for feedback in feedbacks:
    #    if not "doclist" in feedback:
    #        continue
    #    clicks += len([d for d in feedback["doclist"]
    #                   if "clicked" in d and d["clicked"]])

    stats = {
             "query": core.db.db.query.find({"site_id": site_id}).count(),
             "doc": core.db.db.doc.find({"site_id": site_id}).count(),
             "impression": feedbacks.count(),
             "click": clicks,
    }
    return render_template("site/site.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           stats=stats)


@mod.route('/<site_id>/query')
@requires_login
def query(site_id):
    site = core.site.get_site(site_id)
    return render_template("site/query.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           queries=core.db.db.query.find({"site_id": site_id}))


@mod.route('/<site_id>/query/<qid>')
@requires_login
def query_detail(site_id, qid):
    site = core.site.get_site(site_id)
    try:
        historical = core.feedback.get_historical_feedback(qid=qid,
                                                           site_id=site_id)[0]
    except:
        historical = None
    return render_template("site/query_detail.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           historical=historical,
                           query=core.db.db.query.find_one({"site_id": site_id,
                                                            "_id": qid}))


@mod.route('/<site_id>/doc')
@requires_login
def doc(site_id):
    site = core.site.get_site(site_id)
    return render_template("site/doc.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           docs=core.db.db.doc.find({"site_id": site_id}))


@mod.route('/<site_id>/doc/<docid>')
@requires_login
def doc_detail(site_id, docid):
    site = core.site.get_site(site_id)
    stats = {
             "queries": [q
                           for q in core.db.db.query.find({"site_id": site_id})
                           if "doclist" in q and docid in q["doclist"]],
    }
    return render_template("site/doc_detail.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           doc=core.db.db.doc.find_one({"site_id": site_id,
                                                    "_id": docid}),
                           stats=stats)


@mod.route('/<site_id>/disable')
@requires_login
def site_disable(site_id):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('site.home'))
    core.site.disable(site_id)
    flash('Site is disabled.', 'alert-success')
    return redirect(url_for('site.home'))


@mod.route('/<site_id>/enable')
@requires_login
def site_enable(site_id):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('site.home'))
    core.site.enable(site_id)
    flash('Site is enabled.', 'alert-success')
    return redirect(url_for('site.home'))


@mod.route('/<site_id>/unset_robot')
@requires_login
def site_unset_robot(site_id):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('site.home'))
    core.site.unset_robot(site_id)
    flash('Site is set not to be a robot.', 'alert-success')
    return redirect(url_for('site.home'))


@mod.route('/<site_id>/set_robot')
@requires_login
def site_set_robot(site_id):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('site.home'))
    core.site.set_robot(site_id)
    flash('Site is set to be a robot.', 'alert-success')
    return redirect(url_for('site.home'))