from portcullis.models import DataStream

def validate_stream(stream_id, node_id, port_id):
    '''
        Checks to make sure a given stream exists or not. It either checks by using the streams id or by checking the node/port id pairing.

        Paramters:
            stream_id = The id of the DataStream to check
            node_id   = A node id that can be checked with a port id
            port_id   = A port id that can be checked with a node id

        Returns:
            A dictionary with the datastream id upon succesfull verification and an error message otherwise.
            Keys:
                datastream_id = Datastream id or null
                error         = Error message or null
    '''
    
    if(stream_id != None and stream_id != ''):
        stream = DataStream.objects.get(datastream_id = stream_id)

        if(stream):
            return {'datastream_id':stream['datastream_id']}
        else:
            return {'error':"\ndatastream_id %d does not exist in the datastream table.\n" % stream_id}

    elif(node_id != '' and port_id != ''):
        stream = DataStream.objects.get(node_id = self.node_id, port_id = self.port_id)

        if(stream):
            return {'datastream_id':stream['datastream_id']}
        else:
            return {'error':"\nNode id %d and port id %d does not map to an existing datastream id.\n" % {node_id, port_id}}

    return {'error':"Not enough info to uniquely identify a data stream. You must give either a datastream_id or both a node_id and a port_id. Example: \"datastream_id=1\" or \"node_id=1&port_id=3.\"\n\n" }
