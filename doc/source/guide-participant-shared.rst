.. |new| raw:: html

   <span class="label label-success">New</span>


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
