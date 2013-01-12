"""
" portcullis/customExceptions.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" This module contains the definitions of the custom exceptions reported to clients.
"
" (c) 2013 Visgence, Inc., RegionIX Education Cooperative
"""

class SensorReadingCollision(Exception):
    ''' This exception is thrown when attempting to insert a value into the SensorReading table
    ' and a value already exists for that sensor at that timestamp.
    '''
    _code = 506
    
