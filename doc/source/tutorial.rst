.. _installation:

API Installation Tutorial
=========================

.. note:: You may not need to install the API yourself, read the :ref:`guide`.

This tutorial describes how to install, run and develop with the Living Labs
API. 

If all you want is to participate in the Lab, you do not necessarily need any
of the following. Instead you could just go ahead and implement your client
that talks to our API at http://api.living-labs.net/api/ (for the CLEF competition)
or http://api.trec-open-search.org/api (for the TREC OpenSearch competition).
However, the code we provide does include a simple baseline implementation 
that talks to our API and that you may find useful.
Furthermore, if you do install the API/dashboard/.. on your own machine,
debugging your code will become much easier.

In case you have any comments or questions, please do not
hesitate to file an issue here: https://bitbucket.org/living-labs/ll-api/issues.
Or, you can contact the main developer directly at anne.schuth@uva.nl.

Documentation (including this tutorial) can be found here:
http://doc.living-labs.net/en/latest/


Obtain source code
------------------

You can clone the repository that contains all the Living Labs API's code
as follows:

.. sourcecode:: bash

    $ git clone https://bitbucket.org/living-labs/ll-api.git

In case you plan on making changes, please first make a fork through the
bitbucket interface and then clone your own fork. That way, you will be able to
push your changes and to ask for a pull request so that your changes can be
merged back.

Install prerequisites
---------------------

Our code is Python 2.6/2.7 code. It definitely won't run on Python 3.x, and most 
likely not on earlier versions of Python.
If you want to run the API yourself or if you want to run pre-packed clients 
that communicate with an API, then a couple of prerequisites are needed.
However, installing them is easy (if you have pip installed):

.. sourcecode:: bash

    $ sudo pip install -r requirements.txt

If you don't have pip yet, install it using :code:`easy_install pip`. Windows
users may want to read here:
http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows

You may need to install the python-dev package. And it sometimes happens 
(for instance on Windows), that you need to install Numpy/Scipy manually first.

Done?
-----

If you only want to run a client, you have all you need. Clients are pieces of
code that talk to the Living Labs API. We recognize two types of clients:
participants and sites. Example clients are in the repository in the
:code:`ll/clients` directory. See `Running Clients`_.

In case you want to run your own version of the API (for testing purposes),
you'll have to continue.

You don't necessarily have to do that, our API is running here:
http://api.living-labs.net/api/ (for CLEF) or http://api.trec-open-search.org (for TREC OpenSearch).

.. _setup_mongodb:

Setup MongoDB
-------------

If you don't already have MongoDB, you may follow a guide for your operating
system at this page: http://docs.mongodb.org/manual/installation/.
You'll need MongoDB version >=2.6.

Then you can choose to run with or without authentication (without is easier,
but unsecure).

Either way, move to the `ll-api` directory:

.. sourcecode:: bash

    $ cd ll-api


Authenticated
^^^^^^^^^^^^^

To run MongoDB with authentication enabled you can run it with the provided
configuration file config/mongodb.conf (you may have to edit the data path).

First start a MongoDB daemon as follows:

.. sourcecode:: bash

    $ mongod --config config/mongodb.conf

Now, use the :code:`admin` tool to create a database user and database admin,
which you will need later to access the database. Note that these database users
are different from the LivingLabs users you are going to create later.

Replace :code:`USERSECRET` and :code:`ADMINSECRET` by your desired user
and admin passwords and remember them.

.. sourcecode:: bash

    $ ./bin/admin db --setup-db-users --mongodb_db ll --mongodb_user ll --mongodb_user_pw USERSECRET --mongodb_admin admin --mongodb_admin_pw ADMINSECRET

Now, we use the admin tool to generate a configuration file containing the database username and password, which we will need later. Again, replace the passwords!

.. sourcecode:: bash

    $ ./bin/admin db --export-conf-file config/db.ini --mongodb_db ll --mongodb_user ll --mongodb_user_pw USERSECRET

   
The tool will export the database username and password to the :code:`db.ini` file. Remember to never add this file to a code repository,
that would be a severe security threat.

Non-Authenticated
^^^^^^^^^^^^^^^^^

For developing purposes, this is fine. Otherwise, make sure to use
authentication. Start a MongoDB deamon as follows:

.. sourcecode:: bash

    $ mongod


Run the API
-----------
We make a local copy of the user settings file, :code:`config/livinglabs.ini`,
so it is safer to make changes to it later:

.. sourcecode:: bash

    $ cp config/livinglabs.ini config/livinglabs.local.ini

Furthermore, there is a configuration file :code:`ll/core/config.py`, which stores API constants like
web adresses, e-mail adresses and competition deadlines. Depending on the competition you would like
to run this API for (CLEF or TREC OpenSearch), there is a template configuration file template which you could install.

For CLEF, issue:

.. sourcecode:: bash

    $ cp ll/core/config_clef.py ll/core/config.py


For TREC OpenSearch, issue:

.. sourcecode:: bash

    $ cp ll/core/config_trec_opensearch.py ll/core/config.py
    
To start the API, run the following command: 

.. sourcecode:: bash
    
    $ ./bin/api -c config/livinglabs.local.ini config/db.ini

If you want to automatically have the API reload when you change the code (which
is incredibly handy when developing) then run this with :code:`--debug` the
debug flag: 

.. sourcecode:: bash

    $ ./bin/api -c config/livinglabs.local.ini config/db.ini --debug

In general, use :code:`--help` or :code:`-h` for more information.

.. _fill_db:

Fill the Database
-----------------
To fill the database with a standard configuration, including clients and sites, a fixture is available in the `dump` directory. We use the :code:`admin` tool to import this fixture:

.. sourcecode:: bash

    $ ./bin/admin db --import-json dump/ -c config/db.ini

We want to check that the users have been created. Users are clients and sites connecting to the LivingLabs API and should not be confused with the database users created in the :ref:`Setup MongoDB<setup_mongodb>` section. To show all users (clients and sites), issue the following command:

.. sourcecode:: bash 

    $ ./bin/admin user -c config/db.ini --show

You will see the following:

.. sourcecode:: bash

    E0016261DE4C0D61-M6C4AMHHE4WV4OVY uva test@example.com SITE 
    9EA887B684DD5822-JBB2XOCVEGYE7YAZ user1 test1@example.com PARTICIPANT ADMIN
    77DBF9C7A1F70422-EZICBLYSCMMBJWKR user2 test2@example.com PARTICIPANT 

- `uva` is a site, with :code:`sitepass` as its standard password.
- `user1` is a verified participant, which means it has been authorized to connect with sites via the Dashboard. `user1` is also an admin user, so you can use it to change global settings on the Dashboard. Its password is :code:`partpass`.
- `user2` is an unverified participant, it still has to be verified via the Dashboard by an administrator. The standard password for `user2` is :code:`part2pass`.
 
The user e-mail adresses, combined with the mentioned passwords, can be used to log in to the :ref:`Dashboard<dashboard>`. On the dashboard, you can also change the passwords.

Remember the keys as well, you will need them when creating clients in section :ref:`Running Clients<running_clients>`.


.. _running_clients:

Running Clients
---------------

Clients are pieces of code that talk to the Living Labs API. We recognize two
types of clients: participants and sites. Sites are search engines that share
queries, documents and clicks. Participants rank documents for queries using
clicks. Clients need API keys. You can use the keys obtained in the :ref:`Fill the Database<fill_db>`
section or look them up via the :ref:`Dashboard <dashboard>`.


Run a Site
^^^^^^^^^^

To run a site client and upload queries and documents, you can do the following:

.. sourcecode:: bash 

   $ ./bin/client-site --host localhost --key SITEKEY -q -d

This assumes the API runs on :code:`localhost`, your own computer. If the :code:`--host` argument is omitted, a default online API (specified in :code:`ll/core/config.py`) is used.

It will take TREC queries/runs/document (see :code:`-h` for file locations and
how to change them) as a basis. Alternatively, with the :code:`--letor` switch, 
this client will accept Learning to Rank (Letor) data.

Then, to simulate interactions, run the following:

.. sourcecode:: bash 

   $ ./bin/client-site --host localhost --key SITEKEY -s
   
Again, this will take TREC data (qrels) to simulate clicks using a simple
cascade click model. Or, again, with the :code:`--letor` switch, a Learning to
Rank (Letor) data set.

The simple simulator will print the NDCG value of all the rankings it receives
from the API. 

Note that the site client is not at all aware of the participants, the site
client simply talks to the API. So if there are multiple participant clients
present, the API does not know about this and the NDCG will thus reflect the
average performance of all participants. This is by design. For per-participant
statistics, one should use the :ref:`Dashboard <dashboard>`.

If you want to run multiple sites, you should create multiple keys and start
multiple instances that talk to the same API.

For your convenience, you can download learning to rank (Letor) data sets here:

- **GOV**: http://research.microsoft.com/en-us/um/beijing/projects/letor/LETOR3.0/Gov.rar (you'll need files in QueryLevelNorm)
- **OHSUMED**: http://research.microsoft.com/en-us/um/beijing/projects/letor/LETOR3.0/OHSUMED.zip
- **MQ2007**: http://research.microsoft.com/en-us/um/beijing/projects/letor/LETOR4.0/Data/MQ2007.rar (files for supervised learning)
- **MQ2008**: http://research.microsoft.com/en-us/um/beijing/projects/letor/LETOR4.0/Data/MQ2008.rar (files for supervised learning)
- **Yahoo!**: http://webscope.sandbox.yahoo.com/catalog.php?datatype=c
- **MSLR-WEB10K**: http://research.microsoft.com/en-us/um/beijing/projects/mslr/data/MSLR-WEB10K.zip
- **MSLR-WEB30K**: http://research.microsoft.com/en-us/um/beijing/projects/mslr/data/MSLR-WEB30K.zip
- **Yandex Internet Mathematics 2009**: http://imat2009.yandex.ru/academic/mathematic/2009/en/datasets (query identifier need to be parsed out of comment into qid feature)


Run a Participant
^^^^^^^^^^^^^^^^^

To run a simple participant implementation, you can do this, again assuming the API runs on :code:`localhost`:

.. sourcecode:: bash 

   $ ./bin/client-participant --host localhost -k PARTICIPANTKEY -s
   
The API key can be obtained through a procedure explained in `Fill the Database`
or through the :ref:`Dashboard <dashboard>`.

This will run a baseline system that simply greedily reranks by the number of
clicks. Note that you may need to specify the host/port where the API is
running (see :code:`-h` for details on how to do that).

If you want to run multiple participants, you should create multiple keys and
start multiple instances that talk to the same API.

.. _dashboard:

Dashboard Installation
----------------------

.. note:: You may not need to install a Dashboard yourself, read the :ref:`guide`.

If you are running a local version of the API for development, it is a
good idea to also run a dashboard with it.
 
To start the dashboard, fill out the dashboard fields in the local copy of the general LivingLabs
configuration file (:code:`config/livinglabs.local.ini`). In particular, you will need a `recaptcha`
key (see http://www.google.com/recaptcha), that will fill the `recaptchaprivate` and `recaptchapublic` fields.
`csrfsecrettoken` and `secretkey` are both random strings you should generate.

Then run the following command:

.. sourcecode:: bash

    $ ./bin/dashboard -c config/livinglabs.local.ini config/db.ini

In general, use :code:`--help` or :code:`-h` for more information. By default
the dashboard will run on port 5001.

On the Dashboard, you can log in using the users created under :ref:`Fill the Database<fill_db>`. You can also create new users using the Register button. As a participant, you can use the Dashboard to add yourself to one or more sites. If you are an admin, you can verify participants, so they are able to connect with a site.

Advanced options
================
Congratulations! You are done setting up a LivingLabs API including database, dashboard, sites and clients. Now, we will show some more advanced options to customize your environment.

Create users
------------
If there is a :ref:`Dashboard <dashboard>` running, you can create participants
by choosing `Register` on the :ref:`Dashboard <dashboard>`. It is also
possible to create users via the command line, this also enables you
to create site and admin users.

To create an example participant and a site (for development/testing purposes),
you can run the following script: 

.. sourcecode:: bash 

    $ ./bin/admin user -c config/db.ini config/example-data/site.ini --password CHOOSEAPASSWORD
    $ ./bin/admin user -c config/db.ini config/example-data/user.1.ini --password CHOOSEAPASSWORD

The passwords are used for the `Dasboard`.

In return, you will see two API keys, one for a site and one for a participant.
Record the keys as SITEKEY and PARTICIPANTKEY, you'll need them for the clients.

Instead, you can also provide your own details, or perform actions like deleting users and making users admin. See the help on how to do that:

.. sourcecode:: bash 

   $ ./bin/admin user -h

Do not forget to supply the configuration file as an argument, this gives the API the credentials to log in to the MongoDB database.

Export the database
-------------------
You can export the database to create a human-readable json fixture, like the one we use to :ref:`fill the database<fill_db>`.
To create a fixture in the `dump` directory, issue:

.. sourcecode:: bash 

   $ ./bin/admin db --export-json dump -c config/db.ini


Reset the Database
------------------

In case you need a reset, you can simply run this. But, BE CAREFUL, it can not
be undone (or, probably it can, the MongoDB is journalled, but it will not be
trivial).

.. sourcecode:: bash 

   $ ./bin/admin db --clear -c config/db.ini

Do not forget to recreate users (see above).


Remove all runs for a participant
---------------------------------

There can be cases where you may want to remove all runs for a certain participant.
For example, if a participant has a ranking algorithm which is not competitive,
it will only take user impressions from the other participants. The participant
could then request you as administrator to remove the runs.

The admin tool has a :code:`--remove-runs` option to accomplish this. Supply the key
of the participant for which you want to remove all runs.

 .. danger::
    All runs for the given participant will be removed from the :code:`query`
    collection! Sites will thus not be able to find rankings from this participant
    when looking for a query. The runs are still available in the :code:`run`
    collection, but they are not easy to look up from there.

.. sourcecode:: bash

   $ ./bin/admin user --remove-runs -c config/db.ini --key KEY
