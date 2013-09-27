
from sys import stderr
import logging
log = logging.getLogger('debug')

from django.conf import settings

class ErrorLoggingMiddleware(object):
    
    def process_response(self, request, response):

        if int(response.status_code) < 500:
            return response

        msg = 'Server Error: '
        msg += '\n\tRequest Url: ' + request.path + '\n'
        msg += request.read()
        msg += '\n\tResponse:'
        msg += response.content + '\n\n'
        log.warning(msg)
        stderr.write('Logging 500 error in file: ' + settings.LOGGING['handlers']['debug']['filename'])
        stderr.write('\n\n')
        return response


    def process_exception(self, request, exception):
        msg = 'Server Error: '
        msg += '\n\tRequest Url: ' + request.path
        msg += '\n\tRequest Data: ' + request.read()
        msg += '\n\tException: ' + str(exception) + '\n\n'
        stderr.write('Logging 500 error in file: ' + settings.LOGGING['handlers']['debug']['filename'])
        stderr.write('\n\n')

        log.exception(msg)
        return None
