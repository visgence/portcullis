"""
" portcullis/customExceptions.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" This module contains the definitions of the custom exceptions reported to clients.
"
" (c) 2012 Visgence, Inc.
"""

class PortcullisException(Exception):
    _code  = 506

    def getCode(self):
        return self._code

    code = property(getCode)

class SensorReadingCollision(PortcullisException):
    ''' This exception is thrown when attempting to insert a value into the SensorReading table
    ' and a value already exists for that sensor at that timestamp.
    '''
    _code = 507

class InvalidDataStream(PortcullisException):
    '''
    ' This exception is thrown when attempting to insert a value into a datastream that doesn't exist.
    '''
    _code = 508
