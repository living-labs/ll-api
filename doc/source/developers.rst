.. _developer:

Information for developers
==========================
If you would like to modify the LivingLabs API, first follow the API
installation tutorial.

Run end-to-end test
-------------------
After you made changes to the code, you can run an end-to-end test to check if
everything works properly. The test will setup a clean database, run the API
and test a site and participant. Afterwards everything is cleaned
up. To run the test, go to the root directory of the repository and issue:

.. sourcecode:: bash

    $ nosetests


Coding Style
------------
Core functionality should go in ll/core, the API (in ll/api) and Dashboard
(in ll/dashboard) the user this functionality.

Clients (in ll/client) are used for testing purposes and serve as baseline.

We (try to) stick to PEP8: https://www.python.org/dev/peps/pep-0008/ .


Building Documentation
----------------------
.. note::  you probably don't have to build the documentation. A constantly
	updated version is available here: http://doc.living-labs.net/ .

Our documentation is created with Sphinx and comes largely directly from source
code. This makes it very easy to keep the documentation in sync with the code.

If you updated the documentation and want to test it, run these
commands in a shell from the root of the repository:

.. sourcecode:: bash
    
    $ cd doc
    $ make html
    $ open doc/build/html/index.html


If you receive the following error when building the documentation:

.. sourcecode:: bash

    ValueError: unknown locale: UTF-8
    make: *** [html] Error 1

Then, add these lines to your ~/.bash_profile:

.. sourcecode:: bash
    
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8

Replicating the MongoDB database
--------------------------------
To copy the MongoDB database from one server to another, an elegant solution is `replication`. Replication is supported by MongoDB: http://docs.mongodb.org/manual/replication/
The current database is the `primary` database, from which data is copied to the new, `secondary` database.
In this section, we will roughly follow the steps taken in the following tutorial: http://docs.mongodb.org/manual/tutorial/convert-standalone-to-replica-set/
However, we will also take into account the case that users have already been created on the old database and other
specificalities for LivingLabs.

Setup user roles on old database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you have users on your current database, one of the users should get the :code:`clusterManager` role. This will grant this user
the right to initiate the replication set, as soon as Mongo is in replication set mode.

To grant `admin` the :code:`clusterManager` role:

.. sourcecode:: bash

   $ mongo -u admin -p --authenticationDatabase admin
       > use admin
       > db.grantRolesToUser("admin",{role:"clusterManager", db:"admin"})
       > exit

If you have not set up any users, you do not need to set any roles. Logging in using the anonymous user from localhost
will automatically enable you to initiate the replication set.

Set Azure keepalive time
^^^^^^^^^^^^^^^^^^^^^^^^
If you are using a server on Windows Azure, the `TCP keepalive time` will be set too high. This parameter controls
after how many seconds a keepalive signal is sent. If this signal comes too late, the other side can close the connection.

Set a lower keepalive time using the instructions here: http://docs.mongodb.org/ecosystem/platforms/windows-azure/

.. _selinux:
Setup SELinux policy
^^^^^^^^^^^^^^^^^^^^
If you are using a CentOS machine (or another operating system that uses the SELinux security system), you will get into trouble when
starting :code:`mongod` as a service. The SELinux security system can prohibit :code:`mongod` rights, like using certain
ports.

First, temporarily turn off the enforcement of the SELinux rules:

.. sourcecode:: bash

   sudo setenforce 0

Now, run :code:`mongod`. If the problems were caused by SELinux, MongoDB will be able to run. **However, we do not
want to keep the security turned off.** Therefore, we search for the cases where :code:`mongod` violated a rule and
add exceptions for those rules:

.. sourcecode:: bash

   sudo grep mongod /var/log/audit/audit.log | sudo audit2allow -M mypol
   sudo semodule -i mypol.pp

Now, we can turn on the enforcement of SELinux rules again:

.. sourcecode:: bash

   sudo setenforce 1

Change database configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The configuration of both the current and the new database have to be changed, in order to be able to connect with eachother.
This can be done by changing the configuration file and restarting :code:`mongod`, or by restarting :code:`mongod` while supplying options via the command line.
The following options have to be set:

- :code:`replSet`, with as argument the same replication set name for both databases
- :code:`keyFile`, with as argument the path to a keyfile. This keyfile has to be the same for both databases. Generate a keyfile: http://docs.mongodb.org/manual/tutorial/generate-key-file/

The :code:`bindIp` option restricts the access to the database to a certain IP address. Although this may be a bit safer, it is best to remove the option if you experience any trouble connecting.

Initiate replication set
^^^^^^^^^^^^^^^^^^^^^^^^
Now both databases run in replication mode, we should quickly set up the replication set. Sometimes, the database
does not function properly if this has not yet been done.

On the `current` database (important, because we want this one to be `primary`), instantiate the replication set:

Log in to the Mongo shell (in this example with authentication) and execute :code:`rs.initiate()`:

.. sourcecode:: bash

   $ mongo -u admin -p --authenticationDatabase admin
       > rs.initiate()

After a while, the replication set has been instantiated. You can check its status with :code:`rs.status()` and its configuration
with :code:`rs.config()`. You can also give the current member (the old database) a higher priority (for example 10), so it
will be chosen `primary` in elections: http://docs.mongodb.org/manual/tutorial/force-member-to-be-primary/

Now, again in the Mongo shell, add the new database to the replication set. Make sure MongoDB runs on the given external port of the new server:

.. sourcecode:: bash

   > rs.add("ip-address:port")

Congratulations, the replication set has been created and the data will be replicated!


Has the initial sync finished?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
After a while, you might wonder whether the inital sync of files has finished. You can watch the log file of both databases.
Furthermore, you can look dat `rs.status()` in the Mongo shell. It is a good sign if the new database has status `SECONDARY`.

You may see that the data directory size of the old and new database differs. This could be normal. To check that the number
of objects in both databases is the same, compare the output of the following on both databases:

.. sourcecode:: bash

   $ mongo -u ll -p --authenticationDatabase ll
       > use ll
       > db.stats()

Log in with a user (in this case `ll`) which has the right role to perform db.stats().

Using a new data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^
If you change to a new data directory for MongoDB, make sure you have the permissions of the folder right, they should look like this:

.. sourcecode:: bash
   $ ls -la
     drwxr-xr-x.  4 mongod mongod  4096 30 jul 13:56 mongodb

Furthermore, on CentOS, the SELinux rules for this directory also need to be updated, so follow the procedure under :ref:`SELinux`.

Member of the replica set down
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When a majority of the replica set members is down, it can happen that your PRIMARY (original) server, becomes SECONDARY.
This is very unfortunate, because a SECONDARY server does not have write access, so you cannot add queries/runs/etc.

The way to solve this is to remove the inactive members from the replica set configuration and do a forced reconfiguration.
This process is described here:
http://docs.mongodb.org/manual/tutorial/reconfigure-replica-set-with-unavailable-members/
under ``Reconfigure by Forcing the Reconfiguration``. Another possibility may be to stop the replica set altogether, as described under ``Reconfigure by Replacing the Replica Set``
on the same web page
