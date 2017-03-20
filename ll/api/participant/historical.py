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

from flask_restful import Resource, fields, marshal
from .. import api
from .. import core
from .. import ApiResource

doc_fields = {
    "docid": fields.String(),
    "clicked": fields.Float(),
}

feedback_fields = {
    "qid": fields.String(),
    "modified_time": fields.DateTime(),
    "type": fields.String(),
    "doclist": fields.Nested(doc_fields),
}


class Historical(ApiResource):
    def get(self, key, qid):
        """
        Obtain historical feedback for a query. Historical feedback is always
        in the form of aggregated CTR.

        You may specify "all" as the query identifier to obtain
        feedback for all queries.

        :param key: your API key
        :param qid: the query identifier, can be "all"
        :status 403: invalid key
        :status 404: query does not exist
        :status 400: bad request
        :return:
            .. sourcecode:: javascript

                {
                    "feedback": [
                        {"qid": "S-q1",
                         "modified_time": "Sun, 27 Apr 2014 13:46:00 -0000",
                         "type": "ctr",
                         "doclist": [
                             {"docid": "S-d1"
                             "clicked": 0.6},
                             {"docid": "S-d2"},
                             ...
                         ]},
                         ...
                }

        """

        self.validate_participant(key)
        feedbacks = self.trycall(core.feedback.get_historical_feedback,
                                 qid=qid)
        return {"feedback": [marshal(feedback, feedback_fields)
                             for feedback in feedbacks]}


api.add_resource(Historical, '/api/participant/historical/<key>/<qid>',
                 endpoint="participant/historical")
