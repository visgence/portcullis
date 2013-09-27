
from sys import stderr
import logging
log = logging.getLogger('debug')

from django.conf import settings

class ErrorLoggingMiddleware(object):
    
    def process_exception(self, request, exception):
        msg = 'Server Error: '
        msg += '\n\tRequest Url: ' + request.path
        msg += '\n\tRequest Data: ' + request.read()
        msg += '\n\tException: ' + str(exception)

        log.exception(msg)
        return None
