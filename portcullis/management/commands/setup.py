'''
' portcullis/management/commands.setup.py
' Contributing Authors:
'    Jeremiah Davis (Visgence, Inc)
'
' (c) 2013 Visgence, Inc., RegionIx Education Cooperative
'''

# System Imports
from django.core.management import call_command
from django.core.management.base import BaseCommand
from settings import APP_PATH
import git
import sys

# local imports


class Command(BaseCommand):
    help = 'Runs syncdb, git submodule, and sets up an admin user.'

    def handle(self, *args, **options):

        # Make sure we have the current submodules
        sys.stdout.write('Updating git-submodules...')
        sys.stdout.flush()
        repo = git.Repo(APP_PATH)
        repo.submodule_update()
        print 'done.'
        
        call_command('syncdb', interactive=False)

        # ORDER OF FIXTURES MATTERS!! Some have dependencies on others.
        print "Loading fixtures..."
        fixtures = [
            [
                'portcullis/fixtures/portcullisUsers.json',
                'portcullis/fixtures/scalingFunctions.json',
                'portcullis/fixtures/keys.json',
                'portcullis/fixtures/dataStreams.json'
            ]
        ]

        # Load fixtures
        for apps in fixtures:
            for fixture in apps:
                call_command('loaddata', fixture, verbosity=1)
