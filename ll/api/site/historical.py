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


doc_fields = {
    "docid": fields.String(),
    "clicked": fields.Float(),
}

feedback_fields = {
    "site_qid": fields.String(),
    "qid": fields.String(),
    "modified_time": fields.DateTime(),
    "type": fields.String(),
    "doclist": fields.Nested(doc_fields),
}


class Historical(ApiResource):
    def put(self, key, site_qid):
        """
        Store historical user feedback for a query. This is different from live
        feedback, that can be stored through :http:put:`/api/site/feedback/(key)/(sid)`.

        The feedback can be stored multiple times for the same query, the old
        version will be overwritten, it is not additive.

        .. note::

            It is expected that the doclist is the actual doclist that was
            shown to the user. In case multiple doclists were shown for the
            same query, an average ranking may be returned (documents sorted
            by average rank).

        :param key: your API key
        :param site_qid: the sites query identifier
        :reqheader Content-Type: application/json
        :content:
            .. sourcecode:: javascript

                {
                    "type": "ctr",
                    "doclist": [
                        {
                            "site_docid": "b5ee9b2e327493c4fdb24296a94a"
                            "clicked": 0.7,
                        },
                        {
                            "site_docid": "4922d3c4fdb24296a90a20bdd20e"
                            "clicked": 0.4,
                        },
                        ]
                }

        :status 200: stored the feedback
        :status 403: invalid key
        """
        site_id = self.get_site_id(key)
        json = request.get_json(force=True)
        self.check_fields(json, ["doclist", "type"], strict=True)
        feedback = self.trycall(core.feedback.add_historical_feedback,
                                site_id, site_qid, json)
        return {
            "site_qid": feedback["site_qid"],
            "type": feedback["type"],
            "doclist": [marshal(d, doclist_fields)
                        for d in feedback["doclist"]]
            }

    def get(self, key, site_qid):
        """
        Retrieve historical user feedback for a query. This is different from
        live feedback, that can be retrieved
        through :http:get:`/api/site/feedback/(key)/(sid)`.

        :param key: your API key
        :param site_qid: the sites query identifier, or "all"
        :reqheader Content-Type: application/json
        :status 403: invalid key
        :status 404: query does not exist
        :return:
            .. sourcecode:: javascript

                {
                    "type": "ctr",
                    "doclist": [
                        {
                            "site_docid": "b5ee9b2e327493c4fdb24296a94a"
                            "clicked": 0.7,
                        },
                        {
                            "site_docid": "4922d3c4fdb24296a90a20bdd20e"
                            "clicked": 0.4,
                        },
                        ]
                }

        """
        site_id = self.get_site_id(key)
        feedbacks = self.trycall(core.feedback.get_historical_feedback,
                                 site_id=site_id, site_qid=site_qid)
        return {"feedback": [marshal(feedback, feedback_fields)
                             for feedback in feedbacks]}

api.add_resource(Historical, '/api/site/historical/<key>/<site_qid>',
                 endpoint="site/historical")
