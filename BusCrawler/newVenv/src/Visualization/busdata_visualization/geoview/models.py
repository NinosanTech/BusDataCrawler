from django.contrib.gis.db import models

class Occupancy(models.Model):
  occupancy = models.FloatField(max_length=255)
  date = models.DateField()

  class Meta:
    db_table = 'occupancy'

class BusData(models.Model):
  company = models.CharField(max_length=255)
  occupancy = models.ForeignKey(Occupancy, on_delete=models.CASCADE)
  route = models.GeometryField()
  
  class Meta:
        db_table = 'bus_connections'