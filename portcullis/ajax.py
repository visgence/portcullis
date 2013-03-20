"""
" portcullis/ajax.py
" Contributing Authors:
"    Evan Salazar   (Visgence, Inc)
"    Jeremiah Davis (Visgence, Inc)
"    Bretton Murphy (Visgence, Inc)
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
from django.core.exceptions import FieldError, ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from django.db import models, transaction
from django.contrib.auth.models import User as AuthUser
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


@dajaxice_register
def read_source(request, model_name, get_editable):
    '''
    ' Returns all data from a given model as serialized json.
    '
    ' Keyword Args:
    '    model_name - The model name to get serialized data from
    '''

    portcullisUser = check_access(request)
    if isinstance(portcullisUser, HttpResponse):
        return portcullisUser.content
    elif portcullisUser is None:
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)

    read_only = False
    try:
        #Only get the objects that can be edited by the user logged in
        if get_editable and cls.objects.can_edit(portcullisUser):
            objs = cls.objects.get_editable(portcullisUser)
        else:
            objs = cls.objects.get_viewable(portcullisUser)
            read_only = True
    except Exception as e:
        stderr.write('Unknown error occurred in read_source: %s: %s\n' % (type(e), e.message))
        stderr.flush()
        return json.dumps({'errors': 'Unknown error occurred in read_source: %s: %s' % (type(e), e.message)})

    return serialize_model_objs(objs, read_only)


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
    elif portcullisUser is None:
        transaction.rollback()
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    if 'pk' not in data:
        if not cls.objects.can_edit(portcullisUser):
            transaction.rollback()
            return json.dumps({'errors': 'User %s does not have permission to add to this table.' % str(portcullisUser)})
        obj = cls()
    else:
        try:
            obj = cls.objects.get_editable_by_pk(portcullisUser, pk=data['pk'])
            if obj is None:
                transaction.rollback()
                return json.dumps({'errors': 'User %s does not have permission to edit this object' % str(portcullisUser)})
        except Exception as e:
            transaction.rollback()
            return json.dumps({'errors': 'Cannot load object to save: Exception: ' + e.message})

    fields = genColumns(obj)
    m2m = []
    try:
        for field in fields:
            if field['_editable']:

                #save inportant m2m stuff for after object save
                if field['_type'] == 'm2m':
                    m2m.append({
                        'field': field['field'],
                        'model_name': field['model_name'],
                        'app': field['app']
                    })
                    continue

                # Handle empy data
                elif data[field['field']] in [None, ''] and field['_type'] != 'auth_password':
                    if field['_type'] in ['text', 'char', 'color']:
                        setattr(obj, field['field'], '')
                    else:
                        setattr(obj, field['field'], None)

                elif field['_type'] == 'foreignkey':
                    rel_cls = models.loading.get_model(field['app'], field['model_name'])
                    rel_obj = rel_cls.objects.get(pk=data[field['field']]['pk'])
                    if rel_obj.can_view(portcullisUser):
                        setattr(obj, field['field'], rel_obj)
                    else:
                        transaction.rollback()
                        error = 'Error: You do not have permission to assign this object: %s' % rel_obj
                        return json.dumps({'errors': error})

                elif field['_type'] == 'datetime':
                    dt_obj = datetime.strptime(data[field['field']], DT_FORMAT)
                    dt_obj = dt_obj.replace(tzinfo=utc)
                    setattr(obj, field['field'], dt_obj)

                elif field['_type'] == 'auth_password':
                    if data[field['field']] not in [None, '']:
                        obj.set_password(data[field['field']])

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
                    if rel_obj.can_view(portcullisUser):
                        m2m_objs.append(rel_obj)
                    else:
                        transaction.rollback()
                        error = 'Error: You do not have permission to assign this object: %s' % rel_obj
                        return json.dumps({'errors': error})

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
        error = 'In ajax update exception: %s: %s\n' % (type(e), e.message)
        stderr.write(error)
        stderr.flush()
        return json.dumps({'errors': error})

    # Run validations
    try:
        obj.full_clean()
    except ValidationError as e:
        transaction.rollback()
        errors = 'ValiationError '
        for field_name, error_messages in e.message_dict.items():
            errors += ' ::Field: %s: Errors: %s ' % (field_name, ','.join(error_messages))

        return json.dumps({'errors': errors})

    try:
        serialized_model = serialize_model_objs([obj.__class__.objects.get(pk=obj.pk)], True)
    except Exception as e:
        transaction.rollback()
        error = 'In ajax update exception: %s: %s\n' % (type(e), e.message)
        stderr.write(error)
        stderr.flush()
        return json.dumps({'errors': error})

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
    elif portcullisUser is None:
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    try:
        obj = cls.objects.get_editable_by_pk(portcullisUser, data['pk'])
        if obj is None:
            error = "User %s does not have permission to delete this object." % portcullisUser
            return json.dumps({'errors': error})
    except Exception as e:
        error = "There was an error for user %s trying to delete this object: %s" % (portcullisUser, str(e))
        return json.dumps({'errors': error})

    obj.delete()
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
    elif portcullisUser is None:
        return json.dumps({'errors': 'User must be logged in to use this feature.'})

    cls = models.loading.get_model('portcullis', model_name)
    return json.dumps(genColumns(cls))


def serialize_model_objs(objs, read_only):
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

            # What to do when we have a choice field.
            if len(f.choices) > 0:
                default = f.default
                for c in f.choices:
                    choice = {
                        'value': c[0],
                        '__unicode__': c[1]
                    }

                    #See if we can find a choice that is set to this object or
                    #use a default value if not.
                    if c[0] == f.value_from_object(obj) or default == choice['value']:
                        obj_dict[f.name] = choice
                        break

            # Make sure not to send back the actual hashed password.
            if f.model == AuthUser and f.name == 'password':
                password = f.value_to_string(obj)
                if password.startswith('pbkdf2_sha256'):
                    obj_dict[f.name] = 'Hashed'
                else:
                    obj_dict[f.name] = 'Invalid'

            # Types that need to be returned as strings
            elif type(obj_dict[f.name]) not in [dict, list, unicode, int, long, float, bool, type(None)]:
                obj_dict[f.name] = f.value_to_string(obj)

            # Relations
            elif isinstance(f, models.fields.related.ForeignKey) or \
               isinstance(f, models.fields.related.OneToOneField):
                obj_dict[f.name] = {
                    '__unicode__': getattr(obj, f.name).__unicode__(),
                    'pk': f.value_from_object(obj),
                    'model_name': f.rel.to.__name__
                }

            # Datetime Field
            # TODO: expand for other time related fields)
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

    json_data = {'read_only': read_only, 'data': new_objs}
    return json.dumps(json_data, indent=4)


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
            streams = DataStream.objects.get_viewable(portcullisUser)
            streams = streams.filter(name__startswith=name)
            streams = streams.exclude(owner=portcullisUser)
        elif group == 'public':
            streams = DataStream.objects.filter(name__startswith=name)
            viewableStreams = DataStream.objects.get_viewable(portcullisUser)
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
