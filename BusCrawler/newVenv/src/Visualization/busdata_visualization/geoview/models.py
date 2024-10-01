from django.contrib.gis.db import models

# Create your models here.
class Line(models.Model):
  line = models.CharField(max_length=255)
  auslastung_montag = models.CharField(max_length=255)
#   auslastung_montag = models.JSONField
  geometry = models.GeometryField()
  
  class Meta:
        db_table = 'bus_lines'