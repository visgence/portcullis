"""
" api/views/create_shared.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


# System Imports
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta

try:
    import simplejson as json
except ImportError:
    import json

# Local Imports
from check_access import check_access
from portcullis.models import SavedView, Key, DataStream
from graphs.models import SavedDSGraph
from api.utilites import cors_http_response_json


@transaction.commit_manually
@require_POST
def create_saved_view(request):
    '''
    ' Create a savedView and return the token or link for that shared view.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        transaction.rollback()
        return cors_http_response_json({'errors': portcullisUser.content})

    if request.user.is_anonymous():
        transaction.rollback()
        return cors_http_response_json({'errors': "Must be logged in to create saved view"})

    if 'jsonData' not in request.POST:
        transaction.rollback()
        return cors_http_response_json({'errors': "Unrecongnized data"})

    try:
        jsonData = json.loads(request.POST['jsonData'])
    except Exception as e:
        transaction.rollback()
        return cors_http_response_json({'errors': 'Ivalid json: %s' % e.message})

    expires = timezone.now() + timedelta(days=7)
    key = Key.objects.generateKey(portcullisUser, 'Saved view', expires, 20)

    # Create a SavedView object and graphs, and save data.
    savedView = SavedView.objects.create(key = key)

    try:
        start = jsonData['start']
        end = jsonData['end']
        gran = jsonData['granularity']
    except Exception as e:
        transaction.rollback()
        return cors_http_response_json({'errors': 'Error getting json data: %s: %s:' % (type(e), e.message)})

    for graphData in jsonData['graphs']:
        try:
            ds = DataStream.objects.get(id = graphData['ds_id'])
        except DataStream.DoesNotExist:
            transaction.rollback()
            return cors_http_response_json({'errors': 'Datastream does not exist.'})
        except Exception as e:
            transaction.rollback()
            return cors_http_response_json({'errors': 'Unknown error occurred: %s: %s' % (type(e), e.message)})
                               
        # Make sure not to add the key if not the owner.
        if key not in ds.can_read.all() and portcullisUser == ds.owner and not ds.is_public:
            ds.can_read.add(key)
                               
        try:
            reduction = graphData['reduction']
            zoom_start = graphData['zoom_start']
            zoom_end = graphData['zoom_end']
        except Exception as e:
            transaction.rollback()
            return cors_http_response_json({'errors': 'Error getting json data for datastream %d: %s' % (ds.id, e.message)})
        
        graph = SavedDSGraph(datastream = ds, start = start, end = end,
                             reduction_type = reduction, granularity = gran,
                             zoom_start = zoom_start, zoom_end = zoom_end)
        try:
            graph.save()
            savedView.widget.add(graph)
        except Exception as e:
            transaction.rollback()
            return cors_http_response_json({'errors': 'Error saving graph: %s' % e.message})
        
    link = reverse('portcullis-saved-view', args = ['saved_view', key.key])
    transaction.commit()
    return cors_http_response_json({'html':'<a href="%s">%s</a>' % (link, link)})
