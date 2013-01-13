import math

def reduceData(rawData, size, red = 'mean'):
    increment = len(rawData)/size
    data = [None]*(size + len(rawData)%size/increment)
    j = 0
    print 'len(rawData) = %d' % len(rawData)
    for i in range(0, len(rawData), increment):
        print 'j = %d' % j
        data[j] = reductFunc[red](rawData[i:i+increment])
        j += 1
        
    return data

def mean(rawData):
    coord_time = (rawData[len(rawData)-1][0] - rawData[0][0])/2 + rawData[0][0]
    
    # convert to float before taking mean, because float operations are faster than decimal operations
    data = [float(x[1]) for x in rawData]
    coord_data = sum(data)/len(data)
    return [coord_time, coord_data]


def sample(a):
    pass

'''This dictionary stores the function pointers for each of the reduction methods'''
reductFunc = {'mean': mean,
              'sample': sample,
              }

