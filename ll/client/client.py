#!/usr/bin/env python

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

import argparse
import requests
import time
import random
from ll.core.config import config

HEADERS = {'content-type': 'application/json'}


class Client():
    description = "Living Labs for " + config["COMPETITION_NAME"] + " Client"

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.description)
        self.parser.add_argument('--host', dest='host',
                                default=config["URL_API"],
                                help='Host to listen on.')
        self.parser.add_argument('--port', dest='port', default=5000, type=int,
                            help='Port to connect to.')

        self.parser.add_argument('--wait_min', type=int, default=1,
                                help='Minimum simulation waiting time in seconds.')
        self.parser.add_argument('--wait_max', type=int, default=10,
                                help='Max simulation waiting time in seconds.')

        args, _ = self.parser.parse_known_args()

        self.wait_max = args.wait_max
        self.wait_min = args.wait_min
        self.host = "%s:%s/api" % (args.host, args.port)
        if not self.host.startswith("http://"):
            self.host = "http://" + self.host

    def sleep(self, extra=0):
        wait_min = self.wait_min + extra
        wait_max = self.wait_max + extra
        time.sleep(wait_min + (random.random() * (wait_max - wait_min)))

    def get(self, url, tries=0):
        r = requests.get(url, headers=HEADERS)
        if r.status_code == requests.codes.too_many_requests and tries < 15:
            self.sleep(tries + 1)
            return self.get(url, tries=tries + 1)
        elif r.status_code != requests.codes.ok:
            print r.text
            r.raise_for_status()
        else:
            self.sleep()
        return r

    def delete(self, url, tries=0):
        r = requests.delete(url, headers=HEADERS)
        if r.status_code == requests.codes.too_many_requests and tries < 15:
            self.sleep(tries + 1)
            return self.delete(url, tries=tries + 1)
        elif r.status_code != requests.codes.ok:
            print r.text
            r.raise_for_status()
        else:
            self.sleep()
        return r

    def put(self, url, data, tries=0):
        r = requests.put(url, data=data, headers=HEADERS)
        if r.status_code == requests.codes.too_many_requests and tries < 15:
            self.sleep(tries + 1)
            return self.put(url, data, tries=tries + 1)
        elif r.status_code != requests.codes.ok:
            print r.text
            r.raise_for_status()
        else:
            self.sleep()
        return r