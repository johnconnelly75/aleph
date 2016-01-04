from flask import Blueprint, request, redirect
from apikit import jsonify, Pager
import re

from aleph import authz
from aleph.core import url_for, app
from aleph.model import Entity
from aleph.views.cache import etag_cache_keygen
from aleph.search.queries import document_query, get_list_facets
from aleph.search.attributes import available_attributes
from aleph.search import search_documents

from six.moves import urllib

import logging
import uuid

blueprint = Blueprint('search', __name__)

import re
import sys

from aleph.contrib.openoil.search import preprocess_data, exit_redirect


def add_urls(doc):
    doc['archive_url'] = url_for('data.package',
                                 collection=doc.get('collection'),
                                 package_id=doc.get('id'))
    doc['manifest_url'] = url_for('data.manifest',
                                  collection=doc.get('collection'),
                                  package_id=doc.get('id'))
    return doc


def transform_facets(aggregations):
    coll = aggregations.get('all', {}).get('ftr', {}).get('collections', {})
    coll = coll.get('buckets', [])

    lists = {}
    for list_id in get_list_facets(request.args):
        key = 'list_%s' % list_id
        ents = aggregations.get(key, {}).get('inner', {})
        ents = ents.get('entities', {}).get('buckets', [])
        objs = Entity.by_id_set([e.get('key') for e in ents])
        entities = []
        for entity in ents:
            entity['entity'] = objs.get(entity.get('key'))
            if entity['entity'] is not None:
                entities.append(entity)
        lists[list_id] = entities

    attributes = {}
    for attr in request.args.getlist('attributefacet'):
        key = 'attr_%s' % attr
        vals = aggregations.get(key, {}).get('inner', {})
        vals = vals.get('values', {}).get('buckets', [])
        attributes[attr] = vals

    return {
        'sources': coll,
        'lists': lists,
        'attributes': attributes
    }


@blueprint.route('/api/1/query')
def query():
    '''
    Main entry point for search API requests
    '''
    etag_cache_keygen()
    query = document_query(request.args, lists=authz.authz_lists('read'),
                           sources=authz.authz_sources('read'),
                           highlights=True)
    results = search_documents(query)
    pager = Pager(results,
                  results_converter=lambda ds: [add_urls(d) for d in ds])
    data = pager.to_dict()
    data['facets'] = transform_facets(results.result.get('aggregations', {}))
    data = preprocess_data(data)
    return jsonify(data)


@blueprint.route('/api/1/query/attributes')
def attributes():
    '''
    List the metadata available for query results
    (for purposes of filtering, grouping etc)
    '''
    etag_cache_keygen()
    attributes = available_attributes(request.args,
        sources=authz.authz_sources('read'), # noqa
        lists=authz.authz_lists('read')) # noqa
    return jsonify(attributes)

