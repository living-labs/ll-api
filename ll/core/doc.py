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

import datetime
from db import db
import site
import user


def add_doclist(site_id, site_qid, doclist):
    query = db.query.find_one({"site_id": site_id, "site_qid": site_qid})
    if query is None:
        raise LookupError("Query not found: site_qid = '%s'. Add queries "
                          "before adding a doclist." % site_qid)
    store_doclist = []
    for doc in doclist:
        doc_found = get_doc(site_id=site_id, site_docid=doc["site_docid"])
        if not doc_found:
            raise ValueError("Document not found: site_docid = '%s'. Add "
                             "documents before adding a doclist."
                             % doc["site_docid"])
        if "relevance_signals" in doc:
            # szn extension: store relevance signals for this doclist item
            store_doclist.append({
                "_id": doc_found["_id"],
                "relevance_signals": doc["relevance_signals"],
                })
        else:
            store_doclist.append(doc_found["_id"])

    query["doclist"] = store_doclist
    query["doclist_modified_time"] = datetime.datetime.now()
    db.query.save(query)
    return get_doclist(site_id=site_id, site_qid=site_qid)


def get_doclist(site_id=None, site_qid=None, qid=None, key=None):
    q = {}
    if key:
        sites = user.get_sites(key)
        if not sites:
            raise Exception("First signup for sites.")
        q["$or"] = [{"site_id": s} for s in sites]
    if site_id:
        if key and site_id not in sites:
            raise Exception("First signup for site %s." % site_id)
        q["site_id"] = site_id
    if site_qid:
        q["site_qid"] = site_qid
    if qid:
        q["_id"] = qid
    query = db.query.find_one(q)
    if not query:
        if site_qid:
            raise LookupError("Query not found: site_qid = '%s'." % site_qid)
        else:
            raise LookupError("Query not found: qid = '%s'." % qid)
    doclist = []
    for d in query["doclist"]:
        if isinstance(d, basestring):
            doclist.append(db.doc.find_one({"_id": d}))
        else:
            item = db.doc.find_one({"_id": d["_id"]})
            item["relevance_signals"] = d["relevance_signals"]
            doclist.append(item)
    return doclist


def delete_doc(site_id, site_docid):
    existing_doc = db.doc.find_one({"site_id": site_id,
                                    "site_docid": site_docid})
    if existing_doc:
        existing_doc["deleted"] = True
        db.doc.save(existing_doc)
        return True
    return False


def add_doc(site_id, site_docid, doc):
    existing_doc = db.doc.find_one({"site_id": site_id,
                                    "site_docid": site_docid})
    if existing_doc:
        for k in doc:
            existing_doc[k] = doc[k]
        existing_doc["creation_time"] = datetime.datetime.now()
        existing_doc["deleted"] = False
        db.doc.save(existing_doc)
        return existing_doc
    doc["_id"] = site.next_docid(site_id)
    doc["site_id"] = site_id
    doc["site_docid"] = site_docid
    doc["creation_time"] = datetime.datetime.now()
    doc["deleted"] = False
    db.doc.insert(doc)
    return doc


def get_doc(site_id=None, site_docid=None, docid=None, key=None):
    q = {"deleted": {"$ne": True}}
    if key:
        sites = user.get_sites(key)
        if not sites:
            raise Exception("First signup for sites.")
        q["$or"] = [{"site_id": s} for s in sites]
    if site_id:
        if key and site_id not in sites:
            raise Exception("First signup for site %s." % site_id)
        q["site_id"] = site_id
    if site_docid:
        q["site_docid"] = site_docid
    if docid:
        q["_id"] = docid
    return db.doc.find_one(q)


def get_docs(site_id=None, site_docid=None, docid=None, key=None):
    q = {"deleted": {"$ne": True}}
    if key:
        sites = user.get_sites(key)
        if not sites:
            raise Exception("First signup for sites.")
        q["$or"] = [{"site_id": s} for s in sites]
    if site_id:
        if key and site_id not in sites:
            raise Exception("First signup for site %s." % site_id)
        q["site_id"] = site_id
    if site_docid:
        q["site_docid"] = site_docid
    if docid and docid.lower() != "all":
        q["_id"] = docid
    return db.doc.find(q)
