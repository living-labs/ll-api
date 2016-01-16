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

import sys
import argparse
from ll.core.config import config

def logparser():
    for line in sys.stdin:
        try:
            parts = line.split()
            if not parts: continue
            tm = " ".join(parts[0:2])
            url = parts[10]
            ref = parts[11][1:-1]
            yield tm, url, ref
        except:
            continue

argparser = argparse.ArgumentParser(description="Parse uva.nl access logs for "
                                 "queries to send to the Living Labs API.")
argparser.add_argument("--api", "-a", type=str,
                    default=config["URL_API"],
                    help="Living labs API location (default: %(default)s).")
argparser.add_argument("--key", "-k", type=str,
                    default="KEY-123",
                    help="API key (default: %(default)s).")
argparser.add_argument("--upload", "-u", action="store_true",
                    default=False,
                    help="Actually upload to the API (default: %(default)s).")
