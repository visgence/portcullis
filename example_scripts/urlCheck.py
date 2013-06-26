'''
' example_scripts/urlCheck.py
' Contributing Authors:
'   Jeremiah Davis (Visgence, Inc.)
'
' (c) 2013 Visgence, Inc.
'
' This script will send an http response to a given url
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
    raise NotImplemented

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='url The url to check the http status code.')
    parser.add_argument('-d'
                        ,'--datastream_id'
                        ,type=int
                        ,default=None
                        ,help='datastream_id Destination portcullis datastream for the http status code.'
                        )
    parser.add_argument('-u'
                        ,'--portcullisUrl'
                        ,help='portcullisUrl Url for the portcullis data server.'
                        ,default=''
                        )
    parser.add_argument('-k'
                        ,'--auth_token'
                        ,default=''
                        ,help='auth_token Key to allow writing to portcullis datastream.'
                        )
    args = parser.parse_args()
    main(args, parser)
