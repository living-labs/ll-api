.. |new| raw:: html

   <span class="label label-success">New</span>

.. _guide:

Guide for Participants
======================

.. note:: This guide is being updated as it is being used. Please tell us 
			what you think is missing. Our contact details are at the bottom 
			of this page

This guide is meant to be a practical guide to participating in the (CLEF) 
Living Lab. Since we deviate significantly from the typical TREC style 
evaluation setup that most participants are likely to be familiar with, we will
focus primarily on those differences.


Participating in the lab involves following these steps:

#.	Read the `lab description <http://living-labs.net/clef-lab/>`_ and  :ref:`key` below. Make sure you're :ref:`help` when needed.
#.	Sign up

	#. 	If you  take part in CLEF `Register at CLEF <http://clef2015-labs-registration.dei.unipd.it/>`_ 
	#.	`Register with the lab <http://dashboard.living-labs.net/user/register/>`_. You can do this at any moment.
	#.	Sign and send the lab the agreement form. You will receive a link to this form.
	#.	Sign up for individual sites (use-cases) you want to obtain data for. You will receive a link by email to do so.

#.	Implement your method as a client that can talk to the API. Examples are provided. See :ref:`method` below.
#.	Run your client

	#.	The client you implement can use the train queries and historical clicks to learn
	#.	When a testing period starts, download test queries and submit your test runs. Again, the testing period will last for several weeks but there is no need (nor the possibility) to update runs.

#.	If you take part in CLEF

	#.	Write up your findings in a CLEF Working note paper (see schedule below)
	#.	Come to and present your work at `CLEF 2015 in Toulouse, France <http://clef2015.clef-initiative.eu/CLEF2015/>`_ in September 2015.

We hope that all steps but 3. and 4. are self explanatory. Below we detail 
these two steps in Sections :ref:`method` and :ref:`running` respectively.


Schedule
--------

===============	===============================================================================================================
Date 			Description
===============	===============================================================================================================
1 Nov, 2014		Training queries released  (note that you can join any time after this date!) 
27-30 Apr, 2015		Uploading test runs for CLEF Testing period
1 May, 2015		CLEF Testing period begins
15 May, 2015		CLEF Testing period ends
17 May, 2015		:ref:`CLEF Results released <ll4ir-results>` |new|
7 Jun, 2015		CLEF Working notes papers due
15 Jun, 2015		`Additional Testing period begins <http://living-labs.net/challenge/>`_ |new|
30 Jun, 2015		Notification of CLEF Working notes acceptance
15 Jul, 2015		CLEF Camera-ready working notes papers due
7-11 Sep, 2015		Full-day lab session at at `CLEF 2015 in Toulouse, France <http://clef2015.clef-initiative.eu/CLEF2015/>`_
===============	===============================================================================================================


.. _key:

Key Concepts
------------
First some key concepts some of which may come as a surprise and that you
will need to be aware of. These points all surfaced in discussions with
participants. If you think something is missing or if something could be 
explained better or in more detail: please let us know!

Please, read the `lab description <http://living-labs.net/clef-lab/>`_ 
for a general idea of what the lab is about.

Frequent queries and offline processing
	We use frequent queries because these allow participants of the lab to
	prepare their runs offline. Since these queries are frequent, users
	are likely to issue them again at which point a run from participants
	is presented. The major advantage of this approach is that we do not
	require participants to respond to a query within a few milliseconds.
	The down side is that we only consider frequent (head) queries.
	
Train, Test Queries and Testing Periods |new|
	Train queries are there for you to train your system on. Feedback is
	provided for these queries. Test queries on the other hand, are there 
	to evaluate your system. For these queries, you can not change your 
	runs during a testing period and you will not obtain feedback for test
	queries. Outcomes are computed per testing period for test queries. While
	for train queries, outcomes are continuously updated.
	There will `multiple testing period <http://living-labs.net/challenge/>`_ 
	Only one of them is designated as official CLEF testing period.
	
No server required
	Participants do not need to implement nor run a server for serving search
	results to users. This overhead would be a prohibitive burden and is
	lifted by our design that uses head queries for which rankings can be
	pre-computed.
	
Feedback is *not* immediate
	Feedback comes from real users. That means that real users have to enter
	a query that is part of the lab into the search box on the site. They
	then have to click a link and this click has to be fed back into the API.
	There is bound to be a significant delay between submitting a run and
	the feedback becoming available.
	
Feedback is noisy
	Feedback, such as clicks, can not be used as if it were relevance
	judgments. Users click for many reasons. For instance, if a ranking shown
	is really bad, users may start clicking on all links in the rank out of
	despair in which case a click actually signals negative relevance.

Interleaving
	Your ranking may not be shown to users directly, it can be interleaved with
	the current production system of the site. This means that only about half
	the documents shown to a users actually come from your ranking. The other
	half comes from the production ranking.
	This is generally done for two reasons: it allows pairwise comparisons 
	between your ranking and the sites ranking. But also, it reduces the risk
	of showing bad rankings to users.

Simulations 
	Besides real clicks from real users, we provide simulated clicks. While 
	these defy the whole purpose of the living lab setup, they do provide a 
	more constant stream than real clicks do. This may be useful for debugging
	purposes. On the dashboard, simulations are marked with a robot symbol.

Features Instead of Queries and Documents  |new|
	The Web Search (see below) provides features instead of
	actual queries and documents.

.. _scenarios:

Usage Scenarios
---------------

The first edition of the lab focuses on two use-cases and one specific notion 
of what a living lab is, with a view to expanding to other use-cases and other 
interpretations of living labs in subsequent years. Use-cases for the first lab 
are:

Product Search
	On the `REGIO JÁTÉK <http://www.regiojatek.hu/>`_ e-commerce site.
	More detailed information is available on a separate page: :ref:`usecase-regio`. |new|
	
Web Search
	Through `Seznam <http://seznam.cz>`_, a major commercial web search engine.

All three are ad-hoc search tasks and are closely related in terms of their 
general setup. Using a shared API but considering three very different use-cases
allows us to study how well techniques generalize across domains.

The Web Search scenario will slightly  deviate from the other scenarios in that
no actual queries or documents are made available. Instead features are
provided, as in a typical Learning to Rank scenario.


.. _method:

Implement a Client
------------------

We advise you to first familiarize yourself with the :ref:`api-participants`. 

Code that implements a client that talks to this API should approximately take 
the following logical steps:

#.	Obtain queries
#.	For each query, obtain a doclist, a list of candidate documents
#.	For each document in these doclists, obtain the content of the documents
	(if any, some uses cases such as Seznam only provides feature vectors as
	part of the doclist).
#.	Create runs, using your ranking algorithm.
#.	Upload runs
#.	Wait a while to give users a change to interact with your run
#.	Download feedback
#.	Potentially update your run and repeat from 5.

Examples that implement the above steps are included in the code repository
which can be found here: https://bitbucket.org/living-labs/ll-api/

What follows is a *very minimal* example of the above steps. But it should get
you up and running. While we used Python, there is no such requirement for you.
You are free to use any client that communicate with our API.

Note that this really is a very basic example that is purely exploitative. 
It sorts documents only by their click counts. While this may be a reasonable
baseline, it has a huge risk of getting stuck in local optima (unseen documents
never have a change to be clicked). Plus, this approach does not look at the
content of document nor at relevance signals (features). Therefore, it will
not generalize to unseen queries. Nevertheless, it illustrates how to 
communicate with the Living Labs API.

Initialize
~~~~~~~~~~
We start of with some imports and definitions. Replace :code:`KEY` with your own participant key.

.. sourcecode:: python

	import requests
	import json
	import time
	import random
	import datetime # needed for timestamp
	
	HOST = "http://api.living-labs.net/api"
	KEY = "ABC-123"

	QUERYENDPOINT = "participant/query"
	DOCENDPOINT = "participant/doc"
	DOCLISTENDPOINT = "participant/doclist"
	RUNENDPOINT = "participant/run"
	FEEDBACKENDPOINT = "participant/feedback"
	
	HEADERS = {'content-type': 'application/json'}

Obtain Queries
~~~~~~~~~~~~~~
As a participant, you request frequently-issued queries from a site, in order to create
rankings for them. Frequently-issued queries are likely to re-occur and
yield click results in the future.

The :code:`
See also :http:get:`/api/participant/query/(key)`. 

.. sourcecode:: python

	def get_queries():
		r = requests.get("/".join([HOST, QUERYENDPOINT, KEY]), headers=HEADERS)
		if r.status_code != requests.codes.ok:
			print r.text
			r.raise_for_status()
		return r.json()

	queries = get_queries()


Obtain Doclists
~~~~~~~~~~~~~~~
A site has an unranked list of candidate documents for every query. The :code:`get_doclist` method receives the list of documents for one query from the server. The documents for all queries are then stored in the `runs` dictionary.
See also :http:get:`/api/participant/doclist/(key)/(qid)`. 

.. sourcecode:: python

	def get_doclist(qid):
		r = requests.get("/".join([HOST, DOCLISTENDPOINT, KEY, qid]), headers=HEADERS)
		if r.status_code != requests.codes.ok:
			print r.text
			r.raise_for_status()
		return r.json()

	runs = {}
	for query in queries["queries"]:
		qid = query["qid"]
		runs[qid] = get_doclist(qid)


Obtain Feedback and Update Runs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you combine the code above with the following code, the result is a minimal LivingLabs participant. It uploads a ranking to the server which is purely based on the number of clicks a document has received. The content of the documents, which can be received using the `doc` command (:http:get:`/api/participant/doc/(key)/(docid)` ), is not taken into account.

A loop makes sweeps over all queries. For every query, it asks for feedback, updates the ranking and uploads the ranking. You can see that a modified version of the :code:`runs` object is uploaded, which has been received from the site at an earlier stage. The `doclist` is changed to the order of the new ranking. Furthermore, the object is appended with a `runid` field. The `runid` is mandatory, but purely used for your own bookkeeping. In this case, the `runid` is the timestamp of the current ranking update sweep, so it could be used later to identify the time a certain ranking was updated.

See also :http:get:`/api/participant/feedback/(key)/(qid)` and :http:put:`/api/participant/run/(key)/(qid)` 

.. sourcecode:: python

	def get_feedback(qid):
		r = requests.get("/".join([HOST, FEEDBACKENDPOINT, KEY, qid]),
						headers=HEADERS)
		time.sleep(random.random())
		if r.status_code != requests.codes.ok:
			print r.text
			r.raise_for_status()
		return r.json()

	while True:
            # Refresh timestamp when new update of all query rankings
            # is started
            timestamp = datetime.datetime.now().isoformat()
            for query in queries["queries"]:
                    qid = query["qid"]
                    feedbacks = get_feedback(qid)
                    clicks = dict([(doc['docid'], 0) for doc in runs[qid]['doclist']])
                    for feedback in feedbacks['feedback']:
                            for doc in feedback["doclist"]:
                                    if doc["clicked"] and doc["docid"] in clicks:
                                            clicks[doc["docid"]] += 1
                    runs[qid]['doclist'] = [{'docid': docid}
                                            for docid, _ in
                                            sorted(clicks.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]
                    runs[qid]['runid'] = timestamp
                    r = requests.put("/".join([HOST, RUNENDPOINT, KEY, qid]),
                                            data=json.dumps(runs[qid]), headers=HEADERS)

                    if r.status_code != requests.codes.ok:
                            print r.text
                            r.raise_for_status()
                    time.sleep(random.random())

.. _running:

Running a Client
----------------

Once you implemented your ranking algorithm to compete in the LL4IR in the form
of a client that communicates with our API, you can run your during the whole
training period. After that, you will have the change to download the test 
queries for which you can then upload your runs. For this, you will have 24 
hours after downloading the test queries. After these 24 hours, the API
will start evaluating your runs using live data. And at that point, there 
will be no way for participants to update their rankings anymore.


.. _help:

Getting Help
------------

We do our best to run everything smoothly, but given that this is the first
year and the first lab of its kind, you may hit some bumps.

Please let us know if you have any problems.

-	`File an issue <https://bitbucket.org/living-labs/ll-api/issues/new>`_ if 
	you think something is wrong with the API.
-	Ask questions `in this chat room <https://www.hipchat.com/gmkO1RdK1>`_
-	Write an email to `Anne Schuth <mailto:anne.schuth@uva.nl>`_
-	Sign up for the `mailinglist <https://groups.google.com/forum/#!forum/living-labs>`_

If you report issues or ask questions, please provide as many details as you can!

- 	What API endpoint where you calling?
- 	What was response?
- 	What was the HTTP status?
- 	Was there any stacktrace? Please send it along.
-	(How) can you reproduce the problem?

If you are contacting the organizers, it is fine to share a full
HTTP request to the API including your API-key. However, please do not share
this key publicly.

Citation
--------
If you use the API, please refer to `this paper <http://www.anneschuth.nl/wp-content/uploads/2014/08/cikm2014-lleval.pdf>`_: ::

    @inproceedings{Balog2014Head,
		title = {Head First: Living Labs for Ad-hoc Search Evaluation},
		author = {Balog, Krisztian and Kelly, Liadh and Schuth, Anne},
		booktitle = {Proceedings of the 23rd ACM International Conference on Conference on Information and Knowledge Management},
		series = {CIKM '14},
		pages = {1815--1818},
		publisher = {ACM},
		year = {2014},
		url = {http://www.anneschuth.nl/wp-content/uploads/2014/08/cikm2014-lleval.pdf},
		doi = {10.1145/2661829.2661962}
	}
