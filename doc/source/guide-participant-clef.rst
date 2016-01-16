.. |new| raw:: html

   <span class="label label-success">New</span>

.. _guide_participant_clef:

Participant guide for CLEF Living Labs |new|
============================================

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

	#. 	If you  take part in CLEF `Register at CLEF <http://clef2016-labs-registration.dei.unipd.it/>`_
	#.	`Register with the lab <http://dashboard.living-labs.net/user/register/>`_. You can do this at any moment.
	#.	Sign and send the lab the agreement form. You will receive a link to this form.
	#.	Sign up for individual sites (use-cases) you want to obtain data for. You will receive a link by email to do so.

#.	Implement your method as a client that can talk to the API. Examples are provided. See :ref:`method` below.
#.	Run your client

	#.	The client you implement can use the train queries and historical clicks to learn
	#.	When a testing period starts, download test queries and submit your test runs. Again, the testing period will last for several weeks but there is no need (nor the possibility) to update runs.

#.	If you take part in CLEF

	#.	Write up your findings in a CLEF Working note paper (see schedule below)
	#.	Come to and present your work at `CLEF 2016 in Évora, Portugal <http://clef2016.clef-initiative.eu/>`_ in September 2016.

We hope that all steps but 3. and 4. are self explanatory. Below we detail
these two steps in Sections :ref:`method` and :ref:`running` respectively.


Schedule |new|
--------------

===============	===============================================================================================================
Date 			Description
===============	===============================================================================================================
15 Apr, 2016		CLEF Testing period begins
30 Apr, 2016		CLEF Testing period ends
10 May, 2016		CLEF Results released
25 May, 2016		CLEF Working notes papers due
15 May, 2016		`Additional Testing (round #9) period begins <http://living-labs.net/challenge/>`_
17 Jun, 2016		Notification of CLEF Working notes acceptance
1 Jul, 2016		CLEF Camera-ready working notes papers due
5-8 Sep, 2016		Full-day lab session at at `CLEF 2016 in Évora, Portugal <http://clef2016.clef-initiative.eu>`_
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


.. include:: guide-participant-shared.rst