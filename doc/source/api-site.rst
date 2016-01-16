.. _api-sites:

API Reference for Sites
=======================

We provide a basic API for sites. We use the term 'sites' to refer to search
engines that dedicate a (small) part of their traffic to evaluating runs from
participants of the Living Labs.
This API can be used by sites to update the query set, the documents and to 
retrieve  rankings. For each retrieved ranking, the site is expected to provide
feedback. Everything is implemented as HTTP request, and we use the request
types GET, HEAD and PUT. We try to throw appropriate 4XX errors where possible.


.. note:: We have rate limited the API to 300 calls per minute or 10 calls per 
	second, whichever hits first. Please do let us know if this is causing you
	any problems.


Query
-----
From each site, it expected to receive a static sample of (N=100) queries at the
beginning of the challenge. The sample is static in the sense that it will not
change during the challenge. It is important that the sample of queries is
expected to be frequent enough for the duration of the challence. The least
frequent (tail) queries are not very useful for they challenge as they will not
be issued often enough.

This endpoint provides ways to manipulate the set of queries before the 
challenge starts.

.. autoflask:: ll.api.site:app
   :endpoints: site/query
   :undoc-static:
   :include-empty-docstring:

Doclist
-------
Per query, the challenge will provide a preselected doclist of (M=100) documents
to the participants. The selection criteria are up to the site.

As documents to be considered for a query may change over the course of the
challenge, the API provides an endpoint at :http:get:`/api/site/doclist`
to keep the doclist up to date.

.. autoflask:: ll.api.site:app
   :endpoints: site/doclist
   :undoc-static:
   :include-empty-docstring:

Doc
---
The endpoint at :http:get:`/api/site/doc` can be used to update content of
individual documents.

.. autoflask:: ll.api.site:app
   :endpoints: site/doc
   :undoc-static:
   :include-empty-docstring:

Ranking
-------
.. autoflask:: ll.api.site:app
   :endpoints: site/ranking
   :undoc-static:
   :include-empty-docstring:

Feedback
--------
.. autoflask:: ll.api.site:app
   :endpoints: site/feedback
   :undoc-static:
   :include-empty-docstring:

Historical Feedback
-------------------
.. autoflask:: ll.api.site:app
   :endpoints: site/historical
   :undoc-static:
   :include-empty-docstring:
 