"""
" portcullis/ajax.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2013 Visgence, Inc.
"""

# System imports
try:
    import simplejson as json
except ImportError:
    import json

from dajaxice.decorators import dajaxice_register
from django.core import serializers
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import models, transaction
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Context, loader
from django.utils.timezone import utc
from datetime import datetime
from collections import OrderedDict
from sys import stderr
from check_access import check_access

# Local imports
from portcullis.models import DataStream, PortcullisUser
from portcullis.views.crud import genColumns
from settings import DT_FORMAT

# TODO:  All this needs access checkers!!


@dajaxice_register
def read_source(request, model_name):
    '''
    ' Returns all data from a given model as serialized json.
    '
    ' Keyword Args:
    '    model_name - The model name to get serialized data from
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content
    elif request.user.is_anonymous():
        return json.dumps(
            {'errors': 'User must be logged in to use this feature.'}
            )

    cls = models.loading.get_model('portcullis', model_name)

    try:
        #Only get the objects that can be edited by the user logged in
        objs = cls.objects.get_editable(portcullisUser)
    except Exception as e:
        stderr.write('Unknown error occurred in read_source: %s: %s\n' % (type(e), e.message))
        stderr.flush()
        return json.dumps({'errors': 'Unknown error occurred in read_source: %s: %s' % (type(e), e.message)})

    return serialize_model_objs(objs)


@dajaxice_register
@transaction.commit_manually
def update(request, model_name, data):
    '''
    ' Modifies a model object with the given data, saves it to the db and
    ' returns it as serialized json.
    '
    ' Keyword Args:
    '    model_name  - The name of the model object to modify.
    '    data - The data to modify the object with.
    '
    ' Returns:
    '    The modified object serialized as json.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        transaction.rollback()
        return portcullisUser.content
    elif request.user.is_anonymous():
        transaction.rollback()
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    if 'pk' not in data:
        obj = cls()
    else:
        try:
            if cls.objects.is_editable_by_user(portcullisUser, data['pk']):
                obj = cls.objects.get(pk=data['pk'])
            else:
                transaction.rollback()
                return json.dumps({'errors': 'User %s does not have permission to edit this object' % str(portcullisUser)})
        except Exception as e:
            transaction.rollback()
            return json.dumps({'errors': 'Cannot load object to save: Exception: ' + e.message})

    fields = genColumns(obj)
    m2m = []
    try:
        for field in fields:
            if field['_editable'] and data[field['field']] is not None:

                #save inportant m2m stuff for after object save
                if field['_type'] == 'm2m':
                    m2m.append({
                        'field': field['field'],
                        'model_name': field['model_name'],
                        'app': field['app']
                    })
                    continue

                # Do not allow a user to change the owner (unless perhaps admin, but for future...)
                elif field['field'] == 'owner':
                    # Only assign an owner if it is empty, and only to the current user.
                    # Just in case, do not try to reassign the owner if updating...
                    try:
                        getattr(obj, field['field'])
                    except ObjectDoesNotExist as e:
                        setattr(obj, field['field'], portcullisUser)
                    except Exception as e:
                        transaction.rollback()
                        error = 'Error getting the owner field: %s: %s' % (type(e), e.message)
                        stderr.write(error)
                        stderr.flush()
                        return json.dumps({'errors': error})

                elif field['_type'] == 'foreignkey':
                    rel_cls = models.loading.get_model(field['app'], field['model_name'])
                    rel_obj = rel_cls.objects.get(pk=data[field['field']]['pk'])
                    setattr(obj, field['field'], rel_obj)

                elif field['_type'] == 'datetime':
                    if data[field['field']] in [None, '']:
                        setattr(obj, field['field'], None)
                    else:
                        dt_obj = datetime.strptime(data[field['field']], DT_FORMAT)
                        dt_obj = dt_obj.replace(tzinfo=utc)
                        setattr(obj, field['field'], dt_obj)

                else:
                    setattr(obj, field['field'], data[field['field']])

        obj.save()

        try:
            #Get all respective objects for many to many fields and add them in.
            for m in m2m:
                cls = models.loading.get_model(m['app'], m['model_name'])
                m2m_objs = []
                for m2m_obj in data[m['field']]:
                    rel_obj = cls.objects.get(pk=m2m_obj['pk'])
                    m2m_objs.append(rel_obj)

                setattr(obj, m['field'], m2m_objs)

        except Exception as e:
            transaction.rollback()
            error = 'Error setting ManyToMany fields: %s: %s' % (type(e), e.message)
            stderr.write(error)
            stderr.flush()
            transaction.rollback()
            return json.dumps({'errors': error})

    except Exception as e:
        transaction.rollback()
        error = 'In create_datastream exception: %s: %s\n' % (type(e), e.message)
        stderr.write(error)
        stderr.flush()
        return json.dumps({'errors': error})

    serialized_model = serialize_model_objs([obj.__class__.objects.get(pk=obj.pk)])
    transaction.commit()
    return serialized_model


@dajaxice_register
def destroy(request, model_name, data):
    '''
    ' Receive a model_name and data object via ajax, and remove that item,
    ' returning either a success or error message.
    '''

    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content
    elif request.user.is_anonymous():
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    try:
        ds = cls.objects.get(pk=data['pk'], owner=portcullisUser)
    except FieldError:
        ds = cls.objects.get(pk=data['pk'])
    except cls.DoesNotExist:
        error = "User %s attempted to delete an object which does not belong to him/her!"
        error = error % portcullisUser
        stderr.write(error)
        stderr.flush()
        return json.dumps({'errors': error})
    except Exception as e:
        return json.dumps({'errors': 'Could not delete: Exception: %s: %s' % (type(e), e.message)})

    ds.delete()
    return json.dumps({'success': 'Successfully deleted item with primary key: %s' % data['pk']})


@dajaxice_register
def get_columns(request, model_name):
    '''
    ' Return a JSON serialized column list for rendering a grid representing a
    ' model.
    '
    ' Keyword args:
    '   model_name - The name of the model to represent.
    '''
    portcullisUser = check_access(request)

    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content
    elif request.user.is_anonymous():
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    return json.dumps(genColumns(cls))


def serialize_model_objs(objs):
    '''
    ' Takes a list of model objects and returns the serialization of them.
    '
    ' Keyword Args:
    '    objs - The objects to serialize
    '''
    new_objs = []
    for obj in objs:
        fields = obj._meta.fields
        m2m_fields = obj._meta.many_to_many
        obj_dict = {}

        for f in fields:

            #Set value of field for the object.
            obj_dict[f.name] = f.value_from_object(obj)
            if type(obj_dict[f.name]) not in [dict, list, unicode, int, long, float, bool, type(None)]:
                obj_dict[f.name] = f.value_to_string(obj)

            if isinstance(f, models.fields.related.ForeignKey) or \
               isinstance(f, models.fields.related.OneToOneField):
                obj_dict[f.name] = {
                    '__unicode__': getattr(obj, f.name).__unicode__(),
                    'pk': f.value_from_object(obj),
                    'model_name': f.rel.to.__name__
                }
                continue

            elif isinstance(f, models.fields.DateTimeField):
                dt_obj = f.value_from_object(obj)
                if dt_obj is not None:
                    obj_dict[f.name] = f.value_from_object(obj).strftime(DT_FORMAT)

            if '__unicode__' not in obj_dict:
                obj_dict['__unicode__'] = obj.__unicode__()

        for m in m2m_fields:
            m_objs = getattr(obj, m.name).all()
            obj_dict[m.name] = []
            for m_obj in m_objs:
                obj_dict[m.name].append({
                    '__unicode__': m_obj.__unicode__(),
                    'pk': m_obj.pk,
                    'model_name': m.rel.to.__name__
                })

        if 'pk' not in obj_dict:
            obj_dict['pk'] = obj.pk

        new_objs.append(obj_dict)
    return json.dumps(new_objs, indent=4)


@dajaxice_register
def stream_subtree(request, name, group):
    '''
    ' This function will take a partial datastream name, delimited
    ' with '|' and return the next level of the subtree
    ' that matches.
    '
    ' Keyword Args:
    '    name - The 'path' of the subtree (beggining of the name of
    '           the items interested in.)
    '    group - The group to get the subtree for.  Is this a public
    '            group, or an owned group or a
    '            viewable group.
    '''

    portcullisUser = check_access(request)
    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content

    # Check that we are logged in before trying to filter the streams
    if isinstance(portcullisUser, PortcullisUser):
        if group == 'owned':
            streams = DataStream.objects.filter(name__startswith=name)
            streams = streams.filter(owner=portcullisUser)
        elif group == 'viewable':
            streams = DataStream.objects.get_viewable_by_user(portcullisUser)
            streams = streams.filter(name__startswith=name)
            streams = streams.exclude(owner=portcullisUser)
        elif group == 'public':
            streams = DataStream.objects.filter(name__startswith=name)
            viewableStreams = DataStream.objects.get_viewable_by_user(portcullisUser)
            streams = streams.filter(is_public=True).exclude(owner=portcullisUser)
            streams = streams.exclude(id__in=viewableStreams)
        else:
            return json.dumps({'errors': 'Error: %s is not a valid datastream type.' % group})

    elif group == 'public':
        streams = DataStream.objects.filter(name__startswith=name)
        streams = streams.filter(is_public=True)
    else:
        return json.dumps({'errors': 'Error: You must be logged in to see the %s datastream type.' % group})

    level = name.count('|')
    nodes = []
    leaves = {}

    for s in streams:
        split_name = s.name.split('|')
        n_name = split_name[level]

        # Is this a node or leaf?
        if len(split_name) > level + 1:
            if (n_name) not in nodes:
                nodes.append(n_name)
        elif n_name not in leaves:
            leaves[n_name] = s.id
        else:
            return json.dumps({'errors': 'Duplicate name in Database!'})

    t = loader.get_template('stream_subtree.html')
    nodes.sort()
    leaves = OrderedDict(sorted(leaves.items(), key=lambda t: t[0]))
    c = Context({
            'nodes':  nodes,
            'leaves': leaves,
            'path':   name,
            'group':  group
            })
    return json.dumps({'html': t.render(c)})
