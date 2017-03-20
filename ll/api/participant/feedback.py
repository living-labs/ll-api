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
    "clicked": fields.Boolean(default=False),
    "team": fields.String(),
}

feedback_fields = {
    "qid": fields.String(),
    "modified_time": fields.DateTime(),
    "type": fields.String(),
    "runid": fields.String(),
    "doclist": fields.Nested(doc_fields),
}


class Feedback(ApiResource):
    def get(self, key, qid, runid=None):
        """
        Obtain feedback for a query. Only feedback for runs you submitted
        will be returned. So, first submit a run, wait a while to give a user
        the chance to enter the query for which you submitted the run.
        Then, wait even longer to given the site the change to feed the click
        back into our API. As soon as all this happens, the feedback will
        become available here.

        You may specify "all" as the query identifier to obtain
        feedback for all queries.

        Note that you may receive multiple feedbacks for a single query as
        it may have been shown to a user more than once. And even if you
        specify a runid, then the rankings for this runid may have been
        presented to users multiple times.

        Clicks can be either just present (True) or timestamped (list of
        timestamps).

        Feedback is never given for test queries.

        :param key: your API key
        :param qid: the query identifier, can be "all"
        :param runid: *optional*, the runid
        :status 403: invalid key
        :status 404: query does not exist
        :status 400: bad request
        :return:
            .. sourcecode:: javascript

                {
                    "feedback": [
                        {"qid": "S-q1",
                         "runid": "baseline",
                         "modified_time": "Sun, 27 Apr 2014 13:46:00 -0000",
                         "doclist": [
                             {"docid": "S-d1"
                             "clicked": True},
                             {"docid": "S-d2"},
                             ...
                         ]},
                         ...
                }


        In case Team Draft Interleaving was performed at the site, this is
        encoded as follows.

        :content:
            .. sourcecode:: javascript

                {
                "feedback":    [
                    {
                    "qid": "S-q1",
                    "runid": "baseline",
                    "type": "tdi",
                    "doclist": [
                        {
                            "docid": "S-d1",
                            "clicked": true,
                            "team": "site",
                        },
                        {
                            "docid": "S-d4",
                            "clicked": true,
                            "team": "participant",
                        },
                        ]
                    }, ...]
                }
        """

        self.validate_participant(key)
        feedbacks = self.trycall(core.feedback.get_feedback,
                                 userid=key,
                                 qid=qid,
                                 runid=runid)
        return {"feedback": [marshal(feedback, feedback_fields)
                             for feedback in feedbacks]}

    def delete(self, key, qid, runid=None):
        """
        Remove feedback for a query. Only your own feedback will be removed.

        :param key: your API key
        :param qid: the query identifier
        :status 403: invalid key
        :status 404: query does not exist
        :status 400: bad request
        """
        self.validate_participant(key)
        self.trycall(core.feedback.reset_feedback,
                     userid=key, qid=qid)

api.add_resource(Feedback, '/api/participant/feedback/<key>/<qid>/<runid>',
                           '/api/participant/feedback/<key>/<qid>',
                 endpoint="participant/feedback")
