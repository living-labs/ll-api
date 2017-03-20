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

test_period_fields = {'start': fields.DateTime(attribute="START"),
                      'end': fields.DateTime(attribute="END"),
                      'name': fields.String(attribute="NAME"),
                      }

outcome_fields = {"site_id": fields.String(),
                  "qid": fields.String(),
                  "type": fields.String(),
                  "outcome": fields.Float(),
                  "wins": fields.Integer(),
                  "losses": fields.Integer(),
                  "ties": fields.Integer(),
                  "impressions": fields.Integer(),
                  "test_period": fields.Nested(test_period_fields,
                                               default=None,
                                               allow_null=True),
                  }


class Outcome(ApiResource):
    def get(self, key, qid=None):
        """
        Obtain outcome (optionally for a query).

        You may omit or specify "all" as the query identifier to obtain
        feedback for all queries.

        Outcome will be aggregate per site and for test and train queries. If
        specify a query, you will only obtain the outcome for this query.
        Otherwise outcomes are aggregated over all queries.

        The "outcome" is computed as: #wins / (#wins + #losses).
        Where a win is defined as the participant having more clicks on
        documents assigned to it by Team Draft Interleaving than clicks
        on documents assigned to the site.

        Outcome for test queries is restricted to the test period. Train
        queries are not restricted in time.
        See http://living-labs.net/challenge/.

        :param key: your API key
        :param qid: *optional*, the query identifier, can be "all"
        :status 403: invalid key
        :status 404: query does not exist
        :status 400: bad request
        :return:
            .. sourcecode:: javascript

                {
                    "outcomes": [
                        {
                            "type": "test",
                            "test_period": {
                                "start": "Fri, 01 May 2015 00:00:00 -0000"
                                "end": "Sat, 16 May 2015 00:00:00 -0000",
                                "name": "CLEF LL4IR Round #1",
                            },
                            "impressions": 10,
                            "losses": 3,
                            "ties": 5,
                            "wins": 2
                            "outcome": "0.4",
                        },
                        {
                            "qid": "all",
                            "site_id": "S",
                            "type": "train",
                            "test_period": null,
                            "impressions": 10,
                            "losses": 3,
                            "ties": 5,
                            "wins": 2
                            "outcome": "0.4",
                        },
                        ...
                    ]
                }

        """

        self.validate_participant(key)
        outcomes = self.trycall(core.feedback.get_comparison,
                                key,
                                qid=qid)

        return {"outcomes": [marshal(outcome, outcome_fields)
                             for outcome in outcomes]}


api.add_resource(Outcome, '/api/participant/outcome/<key>/<qid>',
                           '/api/participant/outcome/<key>',
                 endpoint="participant/outcome")
