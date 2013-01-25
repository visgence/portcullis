# System Imports
from django.db import models

# Local Imports
from portcullis.models import SavedWidget, DataStream
from graphs.data_reduction import reduction_type_choices

class SavedDSGraph(SavedWidget):
    datastream = models.ForeignKey(DataStream)
    start = models.IntegerField()
    end = models.IntegerField()
    reduction_type = models.CharField(max_length=32, choices=reduction_type_choices())
    granularity = models.IntegerField()
    zoom_start = models.IntegerField()
    zoom_end = models.IntegerField()
