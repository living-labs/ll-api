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

import confargparse
import sys

def application(environ, start_response):
    sys.path.insert(0, environ["location"])
    
    from ll.core.db import db
    from ll.api import app
    import ll.api.participant
    import ll.api.site
        
    description = "Living Labs Challenge's API Server"
    parser = confargparse.ConfArgParser(description=description,
                                        section="main")
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Enable debugging mode.')
    group_flask = parser.add_argument_group("api", section="api")
    group_flask.add_argument('--host', dest='host', default='127.0.0.1',
                        help='Host to listen on.')
    group_flask.add_argument('--port', dest='port', default=5000, type=int,
                        help='Port to listen on.')
    group_mongodb = parser.add_argument_group("mongodb", section="mongodb")
    group_mongodb.add_argument('--mongodb_db', default="ll", type=str,
                        help='')
    group_mongodb.add_argument('--mongodb_user', default=None, type=str,
                        help='')
    group_mongodb.add_argument('--mongodb_user_pw', default=None, type=str,
                        help='')
    args = parser.parse_args(["-c", environ["conf"]])
    
    db.init_db(args.mongodb_db, user=args.mongodb_user,
               password=args.mongodb_user_pw)
    app.debug = args.debug
    
    return app(environ, start_response)
