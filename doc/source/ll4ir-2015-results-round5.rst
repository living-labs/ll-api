.. _ll4ir-results-round5:

LL4IR Round #5 Results
======================

This page presents the LL4IR Round #5 results. This round ran from Sep 15, 2015 till Sep 30, 2015.

#Impressions is the total number of times when rankings (for any of the test queries) from the given team/system have been displayed to users.
The number of wins, losses, and ties are calculated against the production system, where a win is defined as the experimental system having more clicks on results assigned to it by Team Draft Interleaving than clicks on results assigned to the production system.
Outcome is defined as #wins/(#wins+#losses). An outcome value below 0.5 means that the experimental system performed worse than the production system (i.e., in overall, it has more losses than wins).
(Note that we fixed the issue with the expected outcome that we encountered in the :ref:`LL4IR Official Results <ll4ir-results>`.) 

Participants can request the outcomes, for the entire query set (both test and train) as well as for each query individually, via :http:get:`/api/participant/outcome/(key)/(qid)`.

Product search
~~~~~~~~~~~~~~

======== ======= ===== ======= ===== ============
Teamname Outcome #Wins #Losses #Ties #Impressions
======== ======= ===== ======= ===== ============
Baseline 0.4504	 127   155     900   1182
GESIS    0.4182	 138   192     996   1326
IRIT     0.4192	 122   169     969   1260
======== ======= ===== ======= ===== ============


Web search
~~~~~~~~~~
The runs for web search have been removed, therefore, no results are available.



