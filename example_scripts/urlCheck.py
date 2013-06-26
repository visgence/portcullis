#!/usr/bin/env python
'''
' example_scripts/urlCheck.py
' Contributing Authors:
'   Jeremiah Davis (Visgence, Inc.)
'
' (c) 2013 Visgence, Inc.
'
' This script will send an http request to a given url, and then send the status code to
' a portcullis server.
'''

import argparse
import requests
import sys

def main(args, parser=None):
    url = args.url
    ds_id = args.datastream_id
    portcullisUrl = args.portcullisUrl
    auth_token = args.auth_token
    if ds_id is None or portcullisUrl is None or auth_token is None:
        parser.print_help()
        sys.exit(1)

    print 'Sending request to http://%s' % (url,)
    try:
        resp = requests.get('http://' + url)
        status = resp.status_code
    except requests.exceptions.ConnectionError as e:
        print 'Error connecting to http://%s' % (url,)
        status = 0
    print 'Sending status %d to portcullis' % (status,)
    payload = {'auth_token': auth_token
               ,'datastream_id': ds_id
               ,'value': status
               }
    try:
        resp = requests.post('http://' + portcullisUrl + '/api/add_reading/', payload)
    except requests.exceptions.ConnectionError as e:
        print 'Error connecting to portcullis http://%s' % (portcullisUrl,)
        print 'ConnectionError: %s' % e
        sys.exit(1)
    try:
        resp.raise_for_status()
        print resp.text
    except Exception as e:
        print 'Error connecting to portcullis: %s' % (e,)
        sys.exit(1)

    print '\nDone\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group('Required arguments')
    group.add_argument('url', help='The url of which to check the http status code.')
    group.add_argument('-d'
                        ,'--datastream_id'
                        ,type=int
                        ,default=None
                        ,help='Destination portcullis datastream for the http status code.'
                        )
    group.add_argument('-u'
                        ,'--portcullisUrl'
                        ,help='Url for the portcullis data server.'
                        ,default=''
                        )
    group.add_argument('-k'
                        ,'--auth_token'
                        ,default=''
                        ,help='Key to allow writing to portcullis datastream.'
                        )
    # parser.add_argument('t',
    #                     ,'--requestType'
    #                     ,default='GET'
    #                     ,choices=['GET', 'POST']
    #                     ,help='Web request type, `GET\' or `POST\'.'
    #                     )
    args = parser.parse_args()
    main(args, parser)
