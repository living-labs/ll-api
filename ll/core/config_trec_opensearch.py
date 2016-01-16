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
    "EMAIL_FROM": 'organizers@trec-open-search.org',
    "SEND_EMAIL": True,
    "COMPETITION_NAME": "TREC OpenSearch",
    "URL_WEB": "http://trec-open-search.org",
    "URL_API": "http://api.trec-open-search.org/api",
    "URL_DASHBOARD": "http://dashboard.trec-open-search.org",
    "URL_DOC": "http://doc.trec-open-search.org",
    "URL_GIT": "https://bitbucket.org/living-labs/ll-api",
    "URL_REGISTRATION_FORM": "http://living-labs.net/wp-content/uploads/2014/06/LLC14-Application-form.pdf",
    "EMAIL_ORGANIZERS": ["krisztian.balog@uis.no",
                         "liadh.kelly@scss.tcd.ie",
                         "anne.schuth@uva.nl"],
    "TEST_PERIODS": [
                     {"NAME": "TREC OpenSearch 2016 test period",
                      "START": datetime.datetime(2016, 6, 1),
                      "END": datetime.datetime(2016, 7, 15),
                      },
                     ],
    "ROLLBAR_API_KEY": "719ef6f2566f46af9b849fdbc9d43680",
    "ROLLBAR_DASHB0ARD_KEY": "ccf521ba5e49428ebc79bd82b14587fa",
    "ROLLBAR_ENV": "production",
}
