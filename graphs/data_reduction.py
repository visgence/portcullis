"""
" graph/data_reduction.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

import numpy as np

def reduceData(rawData, size, red = 'mean'):
    ''' Take a a list of tuples containing at [0] a timeStamp and at [1] a raw data value from
    ' a sensor reading, and reduce this list to about size datapoints, using different methods.
    ' 
    ' Keyword arguments:
    '  rawData - List of 2-tuples containing (SensorReading.date_entered, SensorReading.sensorValue)
    '  size - The number of datapoints to which to reduce the list. (will not be exact)
    '  red - The reduction method.  Can be 'mean', 'sample', etc.
    '''
    increment = len(rawData)/size
    data = []
    for i in range(0, len(rawData), increment):
        data.append(reductFunc[red](rawData[i:i+increment]))
        
    return data

def incrementMean(data):
    ''' Return the timeCenter of the increment and the mean of the data_values within the increment
    ' as a list of 2 values
    '''
    mid_time = (data[len(data)-1][0] + data[0][0])/2
    
    # convert to float before taking mean, because float operations are faster than decimal operations
    return [mid_time, sum([float(x[1]) for x in data])/len(data)]


def incrementSample(data):
    '''Return the time and datavalue of the first (may be changed in future) element.
    '  This has the effect of reducing the sample size of the data.
    '''
    return [data[0][0], float(data[0][1])]

def incrementMedianSorted(data):
    '''Return the timeCenter of the increment and the median of the data_values within the increment.
    '' Returns a list of 2 values.
    '' We want the timeCenter of the increment because we want the time for the interval over which the
    '' variation occurs.
    '''
    timeCenter = (data[0][0] + data[len(data)-1][0])/2
     
    sortedData = [float(x[1]) for x in data]
    sortedData.sort()
    midPoint = len(sortedData)/2
    if len(sortedData) % 2 == 0:
        return [timeCenter, (sortedData[midPoint] + sortedData[midPoint + 1])/2.0]
    else:
        return [timeCenter, sortedData[midPoint]]

def incrementMax(data):
    '''Return the timeCenter of the increment and the max of the data_values within the increment.
    '' Returns a list of 2 values.
    '' We want the timeCenter of the increment because we want the time for the interval over which the
    '' variation occurs.
    '''
    timeCenter = (data[0][0] + data[len(data)-1][0])/2
    return [timeCenter, max([float(x[1]) for x in data])]

def incrementMin(data):
    '''Return the timeCenter of the increment and the min of the data_values within the increment.
    '' Returns a list of 2 values.
    '' We want the timeCenter of the increment because we want the time for the interval over which the
    '' variation occurs.
    '''
    timeCenter = (data[0][0] + data[len(data)-1][0])/2
    return [timeCenter, min([float(x[1]) for x in data])]

'''This dictionary stores the function pointers for each of the reduction methods'''
reductFunc = {'mean': incrementMean,
              'sample': incrementSample,
              'median': incrementMedianSorted,
              'max': incrementMax,
              'min': incrementMin,
              }

