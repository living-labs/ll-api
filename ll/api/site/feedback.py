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

from flask import request
from flask_restful import fields, marshal
from .. import api
from .. import core
from .. import ApiResource

doclist_fields = {
    "site_docid": fields.String(),
    "title": fields.String(),
}


class Feedback(ApiResource):
    def put(self, key, sid):
        """
        Store user feedback for a session obtained through :http:get:`/api/site/ranking/(key)/(site_qid)`.
        The feedback can be stored multiple times for the same session if more
        feedback comes available.
        In that case, the old feedback will be overwritten, it is not additive.
        So if multiple clicks come in one by one, make sure to include all of 
        them each time you update the feedback.

        .. note::

            It is expected that the doclist is the actual doclist that was
            shown to the user.
            This is important because the site may have had to make a last
            minute decisions not to include a certain document.
            It not obtaining a click is valuable information for a participant.

        :param key: your API key
        :param sid: the session's identifier
        :reqheader Content-Type: application/json
        :content:
            .. sourcecode:: javascript

                {
                    "sid": "s1",
                    "site_qid": "48474c1ab6d3541d2f881a9d4b3bed75",
                    "type": "clicks",
                    "doclist": [
                        {
                            "site_docid": "af1594296a90da20bdd20e40e737"
                            "clicked": true,
                        }, 
                        {"site_docid": "b5ee9b2e327493c4fdb24296a94a"},
                        {"site_docid": "4922d3c4fdb24296a90a20bdd20e"},
                        ]
                }

        In case Team Draft Interleaving was performed, this should be encoded 
        as follows.

        :content:
            .. sourcecode:: javascript

                {
                    "sid": "s1",
                    "site_qid": "4922d3c4fdb24296a90a20bdd20e",
                    "type": "tdi",
                    "doclist": [
                        {
                            "site_docid": "b5ee9b2e327493c4fdb24296a94a"
                            "clicked": true,
                            "team": "site",
                        },
                        {
                            "site_docid": "af1594296a90da20bdd20e40e737"
                            "clicked": true,
                            "team": "participant",
                        },
                        ]
                }

        Historical feedback can be added through :http:get:`/api/site/historical/(key)/(site_qid)`.

        :status 200: stored the feedback
        :status 403: invalid key
        """
        site_id = self.get_site_id(key)
        json = request.get_json(force=True)
        self.check_fields(json, ["doclist", "sid", "type"])
        feedback = self.trycall(core.feedback.add_feedback, site_id, sid, json)
        return {
            "sid": sid,
            "site_qid": feedback["site_qid"],
            "type": feedback["type"],
            "doclist": [marshal(d, doclist_fields)
                        for d in feedback["doclist"]]
            }

api.add_resource(Feedback, '/api/site/feedback/<key>/<sid>',
                 endpoint="site/feedback")
