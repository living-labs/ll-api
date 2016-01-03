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

from pymongo import MongoClient
from collections import OrderedDict
import subprocess
import json
import os

class CoreDatabase(object):
    def __init__(self):
        self.db = None

    def __getattr__(self, name):
        return self.db.__getattr__(name)

    def init_db(self, host, port, db_name, user=None, password=None, authenticationDatabase=None):
        #print("Initialize db ", db_name, "with user", user, "and password", password, "on authbase", authenticationDatabase)
        if self.db == None:
            client = MongoClient(host, port)
            self.db = client[db_name]
            if user and password:
                #print("Now really logging in with", user, "and", password, "on", authenticationDatabase)
                self.db.authenticate(user, password, source=authenticationDatabase)

db = CoreDatabase()


def clear():
    db.user.remove({})
    db.site.remove({})
    db.doc.remove({})
    db.feedback.remove({})
    db.run.remove({})
    
def create_db_admin(host, port, adminname, admin_password):
    # Log in to the 'admin' db, without authentication
    admin_db = CoreDatabase()
    admin_db.init_db(host,port,"admin")
    # Create admin
    admin_db.db.add_user(adminname, admin_password,roles=[{"role": "userAdminAnyDatabase","db":"admin"}])

def create_db_user(host, port, username, user_password, db_name, adminname, admin_password):
    # Log in to the main db, using the admin
    main_db = CoreDatabase()
    main_db.init_db(host, port, db_name,adminname,admin_password,authenticationDatabase="admin")
    # Create user
    main_db.db.add_user(username, user_password,roles = ["readWrite"])

def setup_db_users(host, port, username, user_password, db_name, adminname, admin_password):
    print("Creating admin")
    create_db_admin(host, port, adminname, admin_password)
    print("Creating user")
    create_db_user(host, port, username, user_password, db_name, adminname, admin_password)

def export_json(path, host, port, database, username, password, authentication_database=None):
    # Create binary BSON dump from current database
    host_port = host + ":" + str(port)
    if authentication_database is None:
        subprocess.call(["mongodump","-u",username,"-p", password,"-d",database, "-o",path, "--host", host_port])
    else:
        subprocess.call(["mongodump","-u",username,"-p", password,"-d",database, "-o",path, "--host", host_port, "--authenticationDatabase", authentication_database])
    # Convert BSON file to JSON files
    path_database = os.path.join(path,database)
    files=[]
    for f in os.listdir(path_database):
        if f.endswith(".bson"):
            base = os.path.splitext(f)[0]
            filename=os.path.join(path_database,base)
            with open(filename+ ".json","w") as output_file:
                subprocess.call(["bsondump", filename+".bson"], stdout=output_file)


def import_json(path, host, port, database, username, password, authentication_database=None):
    # Loop over all collections, they have their own json-file and json-metafile
    for collection in ["doc","feedback","historical","query","run","site","system","user"]:
        json_file=os.path.join(path,database,collection)+".json"
        # Import json database file for this collection

        host_port = host + ":" + str(port)
        if authentication_database is None:
            subprocess.call(["mongoimport", "-u", username, "-d", database, "-c", collection,"-p", password,"--file", json_file,"--host", host_port])
        else:
            subprocess.call(["mongoimport", "-u", username, "-d", database, "-c", collection,"-p", password,"--file", json_file,"--host", host_port, "--authenticationDatabase", authentication_database])
        # Import metadata (indexes) for this collection
        if collection != "system":
            import_metadata(path,database,collection)

def import_metadata(path,database,collection):
    json_metafile=os.path.join(path,database,collection) + ".metadata.json"
    f=open(json_metafile,"r")
    structure = json.load(f, object_pairs_hook=OrderedDict)
    attr_list = structure[u"indexes"]
    for item in attr_list:
        if u"key" in item:
            index = item[u"key"]
            if(collection==u"user"):
                db.user.create_index(index.items())
            elif(collection==u"site"):
                db.site.create_index(index.items())
            elif(collection==u"doc"):
                db.doc.create_index(index.items())
            elif(collection==u"feedback"):
                db.feedback.create_index(index.items())
            elif(collection==u"run"):
                db.run.create_index(index.items())
            elif(collection==u"query"):
                db.query.create_index(index.items())
            elif(collection==u"historical"):
                db.historical.create_index(index.items())
