#!/usr/bin/env python

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

import os
import xml.etree.ElementTree as et
import requests
import json
import random
import codecs
from numpy import log2, mean
from client import Client
from ll.core.config import config

PCLICK = {0: 0.05,
          1: 0.5,
          2: 0.95}
PSTOP = {0: 0.2,
         1: 0.5,
         2: 0.9}


QUERYENDPOINT = "site/query"
DOCENDPOINT = "site/doc"
DOCLISTENDPOINT = "site/doclist"
RANKIGNENDPOINT = "site/ranking"
FEEDBACKENDPOINT = "site/feedback"


class Site(Client):
    def __init__(self):
        self.description = "Living Labs " + config["COMPETITION_NAME"] + " Site Client"
        Client.__init__(self)
        path = os.path.dirname(os.path.realpath(__file__))

        self.parser.add_argument('-k', '--key', type=str, required=True,
                            help='Provide a user key.')
        self.parser.add_argument('-q', '--store_queries', action="store_true",
                            default=False,
                            help='Store some queries (needs --query_file and --query_type).')
        self.parser.add_argument('--delete_queries', action="store_true",
                            default=False,
                            help='Delete all queries for this site.')
        self.parser.add_argument('--query_file',
                            default=os.path.normpath(os.path.join(path,
                                                    "../../data/queries.xml")),
                            help='Path to TREC style query file '
                            '(default: %(default)s).')
        self.parser.add_argument('--query_type',
                            default='train',
                            help='Query type: \'train\' or \'test\''
                            '(default: %(default)s).')
        self.parser.add_argument('--letor', action="store_true",
                            default=False,
                            help='Flags that files are in letor format.')
        self.parser.add_argument('-d', '--store_doclist', action="store_true",
                            default=False,
                            help='Store a document list (needs --run_file)')
        self.parser.add_argument('--run_file',
                            default=os.path.normpath(os.path.join(path,
                                                    "../../data/run.txt")),
                            help='Path to TREC style run file '
                            '(default: %(default)s).')
        self.parser.add_argument('-s', '--simulate_clicks', action="store_true",
                            default=False,
                            help="Simulate clicks (needs --qrel_file).")
        self.parser.add_argument('-i', '--iterations', type=int,
                            default=-1,
                            help="Number of iterations for -s")                    
        self.parser.add_argument('--qrel_file',
                            default=os.path.normpath(os.path.join(path,
                                                    "../../data/qrel.txt")),
                            help='Path to TREC style qrel file '
                            '(default: %(default)s).')
        self.parser.add_argument('--docs_dir',
                            default=os.path.normpath(os.path.join(path,
                                                    "../../data/docs")),
                            help='Path to document directory '
                            '(default: %(default)s).')
        args, _ = self.parser.parse_known_args()

        if args.letor:
            if args.store_queries:
                self.store_letor_queries(args.key, args.query_file, args.query_type)
            if args.store_doclist:
                self.store_letor_doclist(args.key, args.run_file)
        else:
            if args.store_queries:
                self.store_queries(args.key, args.query_file, args.query_type)
            if args.store_doclist:
                self.store_doclist(args.key, args.run_file, args.docs_dir)

        if args.simulate_clicks:
            self.simulate_clicks(args.iterations, args.key, args.qrel_file,
                                 args.letor)

        if args.delete_queries:
            self.delete_queries(args.key)

    def store_queries(self, key, query_file, query_type):
        tree = et.parse(query_file)
        topics = tree.getroot()
        queries = {"queries": []}
        for topic in topics.getiterator("topic"):
            qid = topic.attrib["number"]
            query = topic.find("query")
            qstr = query.text
            queries["queries"].append({
                "qstr": qstr,
                "site_qid": qid,
                "type": query_type
            })
        print queries
        url = "/".join([self.host, QUERYENDPOINT, key])
        self.put(url, json.dumps(queries))

    def store_letor_queries(self, key, letor_file):
        current_qid = None
        queries = {"queries": []}
        for line in open(letor_file, "r"):
            qid = line[:line.find("#")].split()[1].split(":")[1]
            if qid != current_qid:
                queries["queries"].append({
                    "qstr": qid,
                    "site_qid": qid,
                })
        url = "/".join([self.host, QUERYENDPOINT, key])
        self.put(url, json.dumps(queries))

    def delete_queries(self, key):
        url = "/".join([self.host, QUERYENDPOINT, key])
        self.delete(url)

    def store_doc(self, key, docid, site_docid, docdir):
        fh = codecs.open(os.path.join(docdir, docid), "r", "utf-8")
        title = fh.readline().strip()
        content = fh.read().strip()
        fh.close()
        doc = {
            "site_docid": site_docid,
            "title": title,
            "content": {"text": content},
            }
        url = "/".join([self.host, DOCENDPOINT, key, site_docid])
        self.put(url, json.dumps(doc))

    def store_doclist(self, key, run_file, docdir):
        def put_doclist(doclist, current_qid):
            site_qid = current_qid
            doclist["site_qid"] = site_qid
            url = "/".join([self.host, DOCLISTENDPOINT, key, site_qid])
            self.put(url, json.dumps(doclist))

        doclist = {"doclist": []}
        current_qid = None
        for line in open(run_file, "r"):
            qid, _, docid, _, _, _ = line.split()
            if current_qid is not None and current_qid != qid:
                put_doclist(doclist, current_qid)
                doclist = {"doclist": []}
            site_docid = docid
            self.store_doc(key, docid, site_docid, docdir)
            doclist["doclist"].append({"site_docid": site_docid})
            current_qid = qid
            self.sleep()
        put_doclist(doclist, current_qid)

    def store_letor_doc(self, key, docid, site_docid):
        tries = 0
        while True:
            doc = {
                "site_docid": site_docid,
                "title": docid,
                "content": {"text": docid},
                }
            url = "/".join([self.host, DOCENDPOINT, key, site_docid])
            self.put(url, data=json.dumps(doc))

    def store_letor_doclist(self, key, letor_file):
        def put_doclist(doclist, current_qid):
            site_qid = current_qid
            doclist["site_qid"] = site_qid
            url = "/".join([self.host, DOCLISTENDPOINT, key, site_qid])
            self.put(url, data=json.dumps(doclist))

        doclist = {"doclist": []}
        current_qid = None
        for line in open(letor_file, "r"):
            firstsplit = line[line.find("#"):]
            docid = firstsplit.split()[2]
            secondsplit = line[:line.find("#")].split()
            qid = secondsplit[1].split(":")[1]
            featureDict = {}
            for pair in secondsplit[2:]:
                featid, feature = pair.split(":")
                featureDict[int(featid)] = float(feature)
            if current_qid is not None and current_qid != qid:
                put_doclist(doclist, current_qid)
                doclist = {"doclist": []}
            site_docid = docid
            self.store_letor_doc(key, docid, site_docid)
            doclist["doclist"].append({"site_docid": site_docid,
                                       "relevance_signals":
                                            featureDict.items()})
            current_qid = qid
        put_doclist(doclist, current_qid)

    def get_ranking(self, key, qid):
        site_qid = qid
        url = "/".join([self.host, RANKIGNENDPOINT, key, site_qid])
        r = self.get(url)
        json = r.json()
        return json["sid"], json["doclist"]

    def store_feedback(self, key, qid, sid, ranking, clicks):
        site_qid = qid
        doclist = {"sid": sid,
                   "site_qid": site_qid,
                   "type": "clicks",
                   "doclist": []}
        for doc, click in zip(ranking, clicks):
            site_docid = doc["site_docid"]
            doclist["doclist"].append({"site_docid": site_docid,
                                       "clicked": click == 1})

        url = "/".join([self.host, FEEDBACKENDPOINT, key, sid])
        self.put(url, data=json.dumps(doclist))

    def get_labels(self, path_file, letor=False):
        labels = {}
        if letor:
            #LETOR file
            for line in open(path_file, "r"):
                splitIndex = line.find("#")
                docid = line[splitIndex:].split()[2]
                secondsplit = line[:splitIndex].split()
                label = secondsplit[0]
                qid = secondsplit[1].split(":")[1]
                if qid not in labels:
                    labels[qid] = {}
                site_docid = docid
                labels[qid][site_docid] = int(label)
        else:
            # QREL file
            for line in open(path_file, "r"):
                qid, _, docid, label = line.split()
                if qid not in labels:
                    labels[qid] = {}
                site_docid = docid
                labels[qid][site_docid] = int(label)
        return labels

    def get_clicks(self, ranking, labels):
        clicks = [0] * len(ranking)
        for pos, doc in enumerate(ranking):
            site_docid = doc["site_docid"]
            label = 0
            if site_docid in labels:
                label = labels[site_docid]
            if label > max(PCLICK.keys()):
                label = max(PCLICK.keys())
            rand = random.random()
            if rand < PCLICK[label]:
                clicks[pos] = 1
                rand = random.random()
                if rand < PSTOP[label]:
                    break
        return clicks

    def evaluate_ranking(self, ranking, labels):
        def get_dcg(orderedlabels):
            dcg = 0.0
            for pos, label in enumerate(orderedlabels):
                dcg += (2. ** label - 1.) / log2(2. + pos)
            return dcg
        orderedlabels = [labels[doc["site_docid"]]
                         if doc["site_docid"] in labels
                         else 0 for doc in ranking]
        idcg = get_dcg(sorted(orderedlabels, reverse=True))
        if idcg == 0.0:
            return 0.0
        return get_dcg(orderedlabels) / idcg

    def evaluate(self, rankings, labels):
        ndcgs = []
        for qid in rankings:
            ndcgs.append(self.evaluate_ranking(rankings[qid], labels[qid]))
        return mean(ndcgs)

    def simulate_clicks(self, n_iterations, key, qrel_file, letor=False):
        labels = self.get_labels(qrel_file, letor)
        rankings = {}
        i = 0
        while (n_iterations==-1 or i < n_iterations):
            qid = random.choice(labels.keys())
            try:
                sid, ranking = self.get_ranking(key, qid)
                rankings[qid] = ranking
                print "NDCG: %.3f" % self.evaluate(rankings, labels)
                # TODO: once in a while, drop a document before return.
                clicks = self.get_clicks(ranking, labels[qid])
                self.store_feedback(key, qid, sid, ranking, clicks)
            except requests.exceptions.HTTPError:
                print "API threw an error, continuing"
            self.sleep()
            i += 1

if __name__ == '__main__':
    site = Site()
