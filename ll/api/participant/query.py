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

from flask_restful import Resource, abort, fields, marshal
from .. import api
from .. import core
from .. import ApiResource

query_fields = {
    "qid": fields.String(attribute="_id"),
    "qstr": fields.String,
    "type": fields.String(default="train"),
    "creation_time": fields.DateTime(),
}


class Query(ApiResource):
    def get(self, key):
        """Obtain the query set for all sites that you have agreed too.
        If you update the sites you agree too through the dashboard, then
        the query set will reflect this.

        Each query is marked with its type. A query can be a train, test or
        eval query. Eval queries are supposed to *not* be evaluated online. So,
        participants will (should) not expect any feedback for them. The
        default query type is "train".

        :param key: your API key
        :status 200: valid key
        :status 403: invalid key
        :return:
            .. sourcecode:: javascript

                {
                    "queries": [
                        {
                            "creation_time": "Mon, 10 Nov 2014 17:42:24 -0000",
                            "qid": "S-q1",
                            "qstr": "jaguar",
                            "type": "train"
                        },
                        {
                            "creation_time": "Mon, 10 Nov 2014 17:42:24 -0000",
                            "qid": "S-q2",
                            "qstr": "apple",
                            "type": "test"
                        }
                    ]
                }

        """
        self.validate_participant(key)
        queries = self.trycall(core.query.get_query, key=key)
        return {"queries": [marshal(q, query_fields) for q in queries
                            if "doclist" in q]}

api.add_resource(Query, '/api/participant/query/<key>',
                 endpoint="participant/query")
