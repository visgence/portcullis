# System Imports
from django.db import models

# Local Imports
from portcullis.models import SavedWidget, DataStream
from graphs.data_reduction import reduction_type_choices

class SavedDSGraph(SavedWidget):
    datastream = models.ForeignKey(DataStream)
    start_date = models.IntegerField()
    end_date = models.IntegerField()
    reduction_type = models.CharField(max_length=32, choices=reduction_type_choices())
    granularity = models.IntegerField()
