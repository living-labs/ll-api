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
    "EMAIL_FROM": 'challenge@living-labs.net',
    "SEND_EMAIL": True,
    "URL_WEB": "http://doc.living-labs.net/en/latest/guide-participant.html",
    "URL_API": "http://api.living-labs.net/api",
    "URL_DASHBOARD": "http://dashboard.living-labs.net/",
    "URL_REACTIVATION": "http://living-labs.net:5001/user/runs",
    "URL_DOC": "http://doc.living-labs.net",
    "URL_GIT": "https://bitbucket.org/living-labs/ll-api/",
    "URL_REGISTRATION_FORM": "http://living-labs.net/wp-content/uploads/2014/06/LLC14-Application-form.pdf",
    "EMAIL_ORGANIZERS": ["krisztian.balog@uis.no",
                         "liadh.kelly@scss.tcd.ie",
                         "anne.schuth@uva.nl"],
    "TEST_PERIODS": [
                     {"NAME": "CLEF LL4IR Round #1",
                      "START": datetime.datetime(2015, 5, 1),
                      "END": datetime.datetime(2015, 5, 16),
                      },
                     {"NAME": "LL4IR Round #2",
                      "START": datetime.datetime(2015, 6, 15),
                      "END": datetime.datetime(2015, 7, 1),
                      },
                     {"NAME": "LL4IR Round #3",
                      "START": datetime.datetime(2015, 7, 15),
                      "END": datetime.datetime(2015, 7, 31),
                      },
                     {"NAME": "LL4IR Round #4",
                      "START": datetime.datetime(2015, 8, 15),
                      "END": datetime.datetime(2015, 8, 31),
                      },
                     {"NAME": "LL4IR Round #5",
                      "START": datetime.datetime(2015, 9, 15),
                      "END": datetime.datetime(2015, 10, 1),
                      },
                     {"NAME": "LL4IR Round #8",
                      "START": datetime.datetime(2015, 12, 15),
                      "END": datetime.datetime(2015, 12, 31),
                      }
                     ],
    "ROLLBAR_API_KEY": "719ef6f2566f46af9b849fdbc9d43680",
    "ROLLBAR_DASHB0ARD_KEY": "ccf521ba5e49428ebc79bd82b14587fa",
    "ROLLBAR_ENV": "production",
    "CLEANUP_INTERVAL_HOURS": 0.005,
    "RUN_AGE_THRESHOLD_DAYS": 0.00001,
    "REACTIVATION_PERIOD_DAYS": 0.01
}
