"""
" graph/data_reduction.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""


def reduceData(rawData, size, red = 'mean'):
    ''' Take a a list of tuples containing at [0] a timeStamp and at [1] a raw data value from
    ' a sensor reading, and reduce this list to about size datapoints, using different methods.
    ' 
    ' Keyword arguments:
    '  rawData - List of 2-tuples containing (SensorReading.timestamp, SensorReading.sensorValue)
    '  size - The number of datapoints to which to reduce the list. (will not be exact)
    '  red - The reduction method.  Can be 'mean', 'sample', etc.
    '''
    #TODO: Custom exception for bad redution type.

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
        return [timeCenter, (sortedData[midPoint] + sortedData[midPoint - 1])/2.0]
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

def incrementMode(data):
    '''Return the timeCenter of the increment and the mode of the data_values within the increment.
    '' Returns a list of 2 values.
    '' We want the timeCenter of the increment because we want the time for the interval over which the
    '' variation occurs.
    '''
    timeCenter = (data[0][0] + data[len(data)-1][0])/2
    data_values = [float(x[1]) for x in data]
    unique_values = {}
    for d in data_values:
        if d in unique_values:
            unique_values[d] += 1
        else:
            unique_values[d] = 1

    max_count = data_values[0]
    for d, count in unique_values.items():
        if count == unique_values[max_count] and d < max_count:
            max_count = d
        elif count > unique_values[max_count]:
            max_count = d
            
    return [timeCenter, max_count]

'''This dictionary stores the function pointers for each of the reduction methods'''
reductFunc = {'mean': incrementMean,
              'sample': incrementSample,
              'median': incrementMedianSorted,
              'max': incrementMax,
              'min': incrementMin,
              'mode': incrementMode
              }

def reduction_type_choices():
    '''
    ' Return a list of tuples of the reduction function dictionary to use
    ' as a choice list in the models.
    '''
    choice_list = []
    for red_type in reductFunc.iterkeys():
        choice_list.append((red_type, red_type.title()))
    return choice_list
