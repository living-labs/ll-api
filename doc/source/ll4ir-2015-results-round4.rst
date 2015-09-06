.. _ll4ir-results-round4:

LL4IR Round #4 Results
======================

This page presents the LL4IR Round #4 results. This round ran from Aug 15, 2015 till Aug 31, 2015.

#Impressions is the total number of times when rankings (for any of the test queries) from the given team/system have been displayed to users.
The number of wins, losses, and ties are calculated against the production system, where a win is defined as the experimental system having more clicks on results assigned to it by Team Draft Interleaving than clicks on results assigned to the production system.
Outcome is defined as #wins/(#wins+#losses). An outcome value below 0.5 means that the experimental system performed worse than the production system (i.e., in overall, it has more losses than wins).
(Note that we fixed the issue with the expected outcome that we encountered in the :ref:`LL4IR Official Results <ll4ir-results>`.) 

Participants can request the outcomes, for the entire query set (both test and train) as well as for each query individually, via :http:get:`/api/participant/outcome/(key)/(qid)`.

Product search
~~~~~~~~~~~~~~

============ ======= ===== ======= ===== ============
Teamname     Outcome #Wins #Losses #Ties #Impressions
============ ======= ===== ======= ===== ============
Expected     0.5
IRIT         0.4654  101   116     767   984
GESIS        0.4292  103   137     804   1044
Baseline     0.3783  87    143     781   1011
============ ======= ===== ======= ===== ============


Web search
~~~~~~~~~~

====================== ======= ===== ======= ===== ============
Teamname               Outcome #Wins #Losses #Ties #Impressions 
====================== ======= ===== ======= ===== ============
Expected               0.5
Exploitative Baseline  0.4500  18    22      134   174
UvA-LambdaMart         0.2059  21    81      89    191
====================== ======= ===== ======= ===== ============
