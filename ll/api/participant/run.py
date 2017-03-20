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
from flask_restful import Resource, fields, marshal
from .. import api
from .. import core
from .. import ApiResource

doc_fields = {
    "docid": fields.String(),
}

run_fields = {
    "creation_time": fields.DateTime(),
    "qid": fields.String(),
    "runid": fields.String(),
    "doclist": fields.Nested(doc_fields)
}


class Run(ApiResource):
    def get(self, key, qid):
        """
        Obtain the last submitted run (ranking) for a specific query.

        :param key: your API key
        :param qid: the query identifier
        :status 200: valid key
        :status 403: invalid key

        :return:
            .. sourcecode:: javascript

                {
                    "qid": "U-q22",
                    "runid": "82"
                    "creation_time": "Wed, 04 Jun 2014 15:03:56 -0000",
                    "doclist": [
                        {
                            "docid": "U-d4"
                        },
                        {
                            "docid": "U-d2"
                        }, ...
                    ],
                }

        """
        self.validate_participant(key)
        run = self.trycall(core.run.get_run, key, qid)
        return marshal(run, run_fields)

    def put(self, key, qid):
        """
        Submit a run (ranking) for a specific query. Note that the runid is
        only for the participants own bookkeeping. It could be any string,
        you may want to use a timestamp. Or the version of your ranker.

        For test queries, a run can only be uploaded outside of test periods.
        An exception to this rule is if you have never uploaded a run for a
        test query. Then, it can be uploaded once during a test period. This
        is to allow participants to join at any moment.
        See test periods here: http://living-labs.net/challenge/.


        :param key: your API key
        :param qid: the query identifier
        :status 200: valid key
        :status 403: invalid key
        :status 409: for test queries, runs can only be uploaded once.


        :reqheader Content-Type: application/json
        :content:
            .. sourcecode:: javascript

                {
                    "qid": "U-q22",
                    "runid": "82"
                    "creation_time": "Wed, 04 Jun 2014 15:03:56 -0000",
                    "doclist": [
                        {
                            "docid": "U-d4"
                        },
                        {
                            "docid": "U-d2"
                        }, ...
                    ],
                }

        """
        self.validate_participant(key)
        run = request.get_json(force=True)
        self.check_fields(run, ["doclist", "runid"])
        run = self.trycall(core.run.add_run, key, qid, run["runid"], run["doclist"])
        return marshal(run, run_fields)

api.add_resource(Run, '/api/participant/run/<key>/<qid>',
                 endpoint="participant/run")
