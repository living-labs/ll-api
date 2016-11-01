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

import datetime

config = {
    "KEY_LENGTH": 32,
    "PASSWORD_LENGHT": 8,
    "EMAIL_FROM": 'trec-os-organizers@googlegroups.com',
    "SEND_EMAIL": True,
    "COMPETITION_NAME": "TREC OpenSearch",
    "URL_WEB": "http://trec-open-search.org",
    "URL_API": "http://api.trec-open-search.org/api",
    "URL_DASHBOARD": "http://dashboard.trec-open-search.org",
    "URL_REACTIVATION": "http://dashboard.trec-open-search.org/user/runs",
    "URL_DOC": "http://doc.trec-open-search.org",
    "URL_GIT": "https://bitbucket.org/living-labs/ll-api",
    "URL_REGISTRATION_FORM": "http://trec-open-search.org/wp-content/uploads/sites/9/2016/01/TRECOpenSearch2016-application-form-editable.pdf",
    "EMAIL_ORGANIZERS": ["krisztian.balog@uis.no",
                         "liadh.kelly@scss.tcd.ie",
                         "anne.schuth@uva.nl"],
    "TEST_PERIODS": [
                     {"NAME": "TREC OpenSearch 2016 test period 1",
                      "START": datetime.datetime(2016, 6, 1),
                      "END": datetime.datetime(2016, 7, 15),
                      },
                     {"NAME": "TREC OpenSearch 2016 test period 2",
                      "START": datetime.datetime(2016, 8, 1),
                      "END": datetime.datetime(2016, 9, 15),
                      },
                     {"NAME": "TREC OpenSearch 2016 test period 3",
                      "START": datetime.datetime(2016, 10, 1),
                      "END": datetime.datetime(2016, 11, 15),
                      },
                     ],
    "ROLLBAR_API_KEY": "719ef6f2566f46af9b849fdbc9d43680",
    "ROLLBAR_DASHB0ARD_KEY": "ccf521ba5e49428ebc79bd82b14587fa",
    "ROLLBAR_ENV": "production",
    "CALC_STATS_INTERVAL_HOURS": 1,
    "CLEANUP_INTERVAL_HOURS": 6,
    "RUN_AGE_THRESHOLD_DAYS": 30,
    "REACTIVATION_PERIOD_DAYS": 7,
    "SEND_EMAIL_RUN_OUTDATED": True,
    "SEND_EMAIL_RUN_OUTDATED": True
}
