
def reduce_data(readings, start, end, reduction_type):
    coord_time = (end - start)/2 + start
    
    if(reduction_type == None or reduction_type == ""):
        reduction_type = 'mean'
    
    coord_data = mean(readings)
    return [coord_time, coord_data]

def mean(readings):
    summation = 0

    for record in readings:
        if(record.sensor_value != None):
            summation = summation + record.sensor_value

    return summation / len(readings)

