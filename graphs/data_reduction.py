def reduce_data(rawData, reduction_type = 'mean'):
    coord_time = (rawData[len(rawData)-1][0] - rawData[0][0])/2 + rawData[0][0]
    
    if(reduction_type == None or reduction_type == ""):
        reduction_type = 'mean'
    
    coord_data = mean([x[1] for x in rawData])
    return [coord_time, float(coord_data)]

def mean(a):
    return sum(a)/len(a)

