.. _api-participants:

API Reference for Participants
==============================

.. note:: Please refer the :ref:`guide` before reading this.


We provide a basic API for participants of the CLEF Living Labs  to perform
several actions such as obtaining a key, queries, documents and feedback. The
API can also be used to update runs. Everything is implemented as HTTP request,
and we use the request types GET, HEAD and PUT. We try to throw appropriate 4XX
errors where possible. Furthermore, the content the API returns when a error is
thrown should help locate the issue. Please let us know when error messages are
not helpful and need clarification.


Note that participants are free to implement their own client to communicate
with this API. However, example clients are provided by the organization.


For all operations, an API key is required. Also, we require you to sign an
agreement. Details on that process will be shared once you sign up.
The dashboard that you can use to obtain an API key is here:
http://dashboard.living-labs.net/

Our API is located at this location: http://api.living-labs.net/api/.

.. note:: We have rate limited the API to 300 calls per minute or 10 calls per 
	second, whichever hits first. Please do let us know if this is causing you
	any problems.



.. note:: We may sometimes restart our API. You may notice this because the API
	is down for a few seconds (up to a few minutes). Please implement your 
	client in such a way that this will not cause problems (i.e., add a retry
	loop with a small sleep to all the API calls).

Query
-----
From each site that a participant signed up for (see 
http://dashboard.living-labs.net/user/sites/), a sample of (N=100) queries is made
available. This endpoint allows for downloading these queries.

After the train phase, new queries (and doclists) will be made available.

.. note:: We kindly ask you to not enter any of the provided queries
    into the search engines for testing purposes (unless, of course
    you have an actual information need that translates in any of the
    queries).
    As we are not aware of your the IP addresses you may use for these
    request, we have no means of filtering such queries out. In
    particular, for the smaller engines such test issues of queries
    might severely impact the usefulness of our challenge. We will,
    however, monitor for strange behavior.


.. autoflask:: ll.api.participant:app
   :endpoints: participant/query
   :undoc-static:
   :include-empty-docstring:


.. _api-participants_doclist:

Doclist
-------
For each query, there is a fixed set of documents available. These documents
are selected by the site. And this selection may change over time. Therefore,
participants should update the doclist for a query on a regular (daily?) 
basis.

For some use cases, the doclist will contain relevance signals (also referred
to as features, or ranking signals). These are always sparse representations, 
missing values can be assumed to be zeros. The relevance signals can be query
only, document only, or query document dependent. 
For these uses cases, the actual query and document content are generally not
provided.
The use cases that do not have relevance signals, will need to provide query
and document content.

.. autoflask:: ll.api.participant:app
   :endpoints: participant/doclist
   :undoc-static:
   :include-empty-docstring:


Doc
---
When a use case does not define relevance signals for each query document pair
then this is where the content of documents is made available.

.. autoflask:: ll.api.participant:app
   :endpoints: participant/doc, participant/docs
   :undoc-static:
   :include-empty-docstring:


Run
---
Runs (TREC terminology) are just rankings of document ids as shown to actual
users. Participants can keep updating their runs. They also have the option
of updating an identifier for the run. This identifier is then used in the
feedback that is returned.

.. autoflask:: ll.api.participant:app
   :endpoints: participant/run
   :undoc-static:
   :include-empty-docstring:

Feedback
--------
.. autoflask:: ll.api.participant:app
   :endpoints: participant/feedback
   :undoc-static:
   :include-empty-docstring:
   

.. _api-participants_outcome:
 
Outcome
-------
.. autoflask:: ll.api.participant:app
   :endpoints: participant/outcome
   :undoc-static:
   :include-empty-docstring: 
  

Historical Feedback
-------------------
.. autoflask:: ll.api.participant:app
   :endpoints: participant/historical
   :undoc-static:
   :include-empty-docstring:
   
