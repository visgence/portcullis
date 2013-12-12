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
import json
import requests
import sys


def main(args, parser=None):
    url = args.url
    uuid = args.uuid
    portcullisUrl = args.portcullisUrl
    if uuid is None or portcullisUrl is None:
        parser.print_help()
        sys.exit(1)

    print 'Sending request to http://%s' % (url,)
    try:
        resp = requests.get('http://' + url, timeout=120)
        status = resp.status_code
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        print 'Error connecting to http://%s' % (url,)
        print 'Exception: %s' % e
        status = 0
    print 'Sending status %d to %s' % (status, portcullisUrl)
    payload = [[uuid, status]]

    try:
        resp = requests.post('http://' + portcullisUrl + '/api/readings/', json.dumps(payload), timeout=120)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        sys.stderr('Error connecting to portcullis http://%s\n' % (portcullisUrl,))
        sys.stderr('ConnectionError: %s\n' % e)
        sys.stderr.flush()
        sys.exit(1)
    try:
        resp.raise_for_status()
        print resp.text
    except Exception as e:
        sys.stderr('Error connecting to portcullis: %s\n' % (e,))
        sys.stderr.flush()
        sys.exit(1)

    print '\nDone\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group('Required arguments')
    group.add_argument('url', help='The url of which to check the http status code.')
    group.add_argument('-d'
                        ,'--uuid'
                        ,default=None
                        ,help='Destination portcullis datastream for the http status code.'
                        )
    group.add_argument('-u'
                        ,'--portcullisUrl'
                        ,help='Url for the portcullis data server.'
                        ,default=None
                        )
    args = parser.parse_args()
    main(args, parser)
