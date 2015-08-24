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

import unittest
import subprocess
import signal
import os
import shutil
import tempfile
import time

MONGODB_CONFIG = "config/mongodb.conf"
LL_CONFIG = "config/livinglabs.ini"
USER = "ll"
USER_PWD = "USERSECRET"
DB_NAME = "ll"
ADMIN = "admin"
ADMIN_PWD = "ADMINSECRET"
DUMP_PATH = "dump"

# Site and participant keys. The following keys agree with the users which
# are created by importing the database fixture:
# http://doc.living-labs.net/en/latest/tutorial.html#fill-the-database
# You can supply your own keys here
SITE_KEY = "E0016261DE4C0D61-M6C4AMHHE4WV4OVY"
PARTICIPANT_KEY = "9EA887B684DD5822-JBB2XOCVEGYE7YAZ"
HOST = "localhost"
N_ITERATIONS = 5  # number of iterations site or participant runs


class TestLL(unittest.TestCase):
    _multiprocess_shared_ = True

    @classmethod
    def setUpClass(self):
        self.mongo_pid = 0
        self.api_process = None

        # Create temporary directory for clean database and config files
        self.tempdir = tempfile.mkdtemp()
        db_dir = os.path.join(self.tempdir, "db")
        os.makedirs(db_dir)
        config_dir = os.path.join(self.tempdir, "config")
        os.makedirs(config_dir)
        ll_db_config = os.path.join(config_dir, "db.ini")
        # Launch mongod
        print("Launch MongoDB")
        mongo_output = subprocess.check_output(["mongod", "--fork", "--syslog",
                                                "--config", MONGODB_CONFIG,
                                                "--dbpath", db_dir])  # overriding dbpath from config file
        # Real Mongo process will be forked, save for pid from output
        for word in mongo_output.split():
            if word.isdigit():
                self.mongo_pid = int(word)

        # Set up MongoDB users
        print("Setup MongoDB users")
        subprocess.call(["./bin/admin", "db", "--setup-db-users",
                         "--mongodb_db", DB_NAME, "--mongodb_user", USER,
                         "--mongodb_user_pw", USER_PWD,
                         "--mongodb_admin", ADMIN,
                         "--mongodb_admin_pw", ADMIN_PWD])
        # Save to configuration file
        subprocess.call(["./bin/admin", "db", "--mongodb_db", DB_NAME,
                         "--mongodb_user", USER, "--mongodb_user_pw", USER_PWD,
                         "--export-conf-file", ll_db_config])
        # Start the API
        self.api_process = subprocess.Popen(["./bin/api",
                                             "-c", LL_CONFIG, ll_db_config,
                                             "--debug"])
        time.sleep(3) # wait for API to load
        
        # Fill database with users
        subprocess.call(["./bin/admin", "db", "--import-json", DUMP_PATH,
                         "-c", ll_db_config])

    def test_site(self):
        print("Test site")
        subprocess.call(["./bin/client-site", "--host", HOST, "--key", SITE_KEY,
                         "-q", "-d",
                         "--wait_max", "0",
                         "--wait_min", "0"])
        print("Simulate site")
        site_output = subprocess.check_output(["./bin/client-site",
                                               "--host", "localhost",
                                               "--key", SITE_KEY,
                                               "-s",
                                               "--iterations", str(N_ITERATIONS),
                                               "--wait_max", "0",
                                               "--wait_min", "0"])
        for line in site_output.split("\n"):
            if len(line) > 0:
                if line.split()[0] != "NDCG:":
                    raise ValueError("Unexpected site output:", line)
        return True
    
    def test_participant(self):
        print("Simulate participant")
        participant_output = subprocess.check_output(["./bin/client-participant",
                                                      "--host", HOST,
                                                      "--key", PARTICIPANT_KEY,
                                                      "-s",
                                                      "--iterations",
                                                      str(N_ITERATIONS),
                                                      "--wait_max", "0",
                                                      "--wait_min", "0"])
        print participant_output
        for line in participant_output.split("\n"):
            if len(line) > 0:
                first = line[0]
                last = line[-1]
                if not (first == "{" and last == "}"):
                    raise ValueError("Unexpected participant output:", line)
        return True

    @classmethod
    def tearDownClass(self):
        print("Teardown")
        
        # Kill api
        self.api_process.kill()
        # Kill mongo
        os.kill(self.mongo_pid, signal.SIGKILL)
        
        # Remove testdb directory
        shutil.rmtree(self.tempdir)
