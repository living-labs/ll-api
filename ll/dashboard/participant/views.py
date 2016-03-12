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
import pickle
import os
from .. import core, requires_login

mod = Blueprint('participant', __name__, url_prefix='/participant')


@mod.route('/')
@requires_login
def home():
    participants = core.user.get_participants()
    return render_template("participant/participants.html", user=g.user,
                           participants=participants, config=core.config.config)


@mod.route('/<email>')
@requires_login
def participant(email):
    participant = core.user.get_user_by_email(email)
    #clicks = 0
    #for feedback in feedbacks:
    #    if not "doclist" in feedback:
    #        continue
    #    clicks += len([d for d in feedback["doclist"] if d["clicked"]])

    stats = {
             "run": 0,
             "impression": 0,
             #"click": 0,
             "sites": [],
    }

    stats_file = "stats_participant_" + participant["_id"] + ".p"

    if os.path.isfile(stats_file):
        stats = pickle.load(open(stats_file,"rb"))

    return render_template("participant/participant.html",
                           user=g.user,
                           participant=participant,
                           stats=stats,
                           config=core.config.config)


@mod.route('/<email>/delete')
@requires_login
def participant_delete(email):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('participant.home'))
    participant = core.user.get_user_by_email(email)
    core.user.delete_user(participant["_id"])
    flash('Participant is deleted.', 'alert-success')
    return redirect(url_for('participant.home'))


@mod.route('/<email>/admin')
@requires_login
def participant_admin(email):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('participant.home'))
    participant = core.user.get_user_by_email(email)
    core.user.set_admin(participant["_id"])
    flash('Participant is admin.', 'alert-success')
    return redirect(url_for('participant.home'))


@mod.route('/<email>/verify')
@requires_login
def participant_verify(email):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('participant.home'))
    participant = core.user.get_user_by_email(email)
    core.user.verify_user(participant["_id"])
    flash('Participant is verified.', 'alert-success')
    return redirect(url_for('participant.home'))


@mod.route('/<email>/unverify')
@requires_login
def participant_unverify(email):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('participant.home'))
    participant = core.user.get_user_by_email(email)
    core.user.unverify_user(participant["_id"])
    flash('Participant is unverified.', 'alert-success')
    return redirect(url_for('participant.home'))



@mod.route('/<email>/form')
@requires_login
def participant_form(email):
    if not g.user["is_admin"]:
        flash('You need to be admin', 'alert-warning')
        return redirect(url_for('participant.home'))
    participant = core.user.get_user_by_email(email)
    core.user.send_form_email(participant)
    flash('Form email is sent.', 'alert-success')
    return redirect(url_for('participant.home'))


@mod.route('/<site_id>/query')
@requires_login
def query(site_id):
    site = core.site.get_site(site_id)
    return render_template("participant/query.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           queries=core.db.db.query.find({"site_id": site_id}))


@mod.route('/<site_id>/query/<qid>')
@requires_login
def query_detail(site_id, qid):
    site = core.site.get_site(site_id)
    return render_template("participant/query_detail.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           query=core.db.db.query.find_one({"site_id": site_id,
                                                            "_id": qid}))


@mod.route('/<site_id>/doc')
@requires_login
def doc(site_id):
    site = core.site.get_site(site_id)
    return render_template("participant/doc.html",
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
    return render_template("participant/doc_detail.html",
                           user=g.user,
                           site=site,
                           config=core.config.config,
                           doc=core.db.db.doc.find_one({"site_id": site_id,
                                                    "_id": docid}),
                           stats=stats)
