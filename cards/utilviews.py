# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Min, Count
from django.shortcuts import redirect
from django.http import Http404
from django.db import connection
from django.db import IntegrityError
import collections
from django.core.urlresolvers import reverse
from haystack.query import SearchQuerySet
from django.conf import settings

import random
import operator
import os
import os.path
import json

from cards.models import Card, CardManager, SearchPredicate, SortDirective, BaseCard
from cards.models import Mark
from cards.models import PhysicalCard

import logging


def cardclustertest(request, test_id=0):
    context = {}
    context['test_number'] = test_id
    # This part really isn't used. Real goal here is the cluster definitions, which is below
    pcid_list = list()

    test_dir = os.path.join('/tmp/clusters/test_{:03d}'.format(int(test_id)))
    #/tmp/clusters/test_000/clusters/
    filelist = os.listdir(os.path.join(test_dir, 'pcards'))
    for filename in filelist:
        if 'physicalcard_' in filename:
            pcid_list.append(filename[len('physicalcard_'): len(filename)])
    context['physicalcard_id_list'] = pcid_list

    # Cluster definitions...
    clustered_cards = {}
    cluster_dir = os.path.join(test_dir, 'clusters')
    filelist = os.listdir(cluster_dir)
    for filename in filelist:
        if 'cluster_' in filename:
            cluster_id = filename[len('cluster_'): len(filename)]
            with open(os.path.join(cluster_dir, filename), 'r') as clustfile:
                # expecting a physical card id (an int) on each line of this file
                pc_ids = clustfile.readlines()
            clustered_cards[cluster_id] = PhysicalCard.objects.filter(id__in=pc_ids)
    context['clustered_cards'] = clustered_cards
    context['metrics'] = {}
    try:
        context['metrics'] = json.load(open(os.path.join(test_dir, 'metrics')))
    except Error:
        pass
    return render(request, 'cards/clustertest.html', context)
