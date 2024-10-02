from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.serializers import serialize
from django.shortcuts import render
from .models import BusData, Occupancy
from shapely.geometry import shape
from shapely import wkt
from django.shortcuts import get_object_or_404
import json
# import pdb; pdb.set_trace()

def geoview(request):
  connections = BusData.objects.all()
  data = serialize('geojson', connections, geometry_field='route', fields=('company', 'occupancy'))
  # print(data)
  context = {
    'lines': data,
  }
  return render(request, 'index.html', context)

def get_bus_data(request):
  occupancies = get_object_or_404(Occupancy)
  connections = BusData.objects.filter(occupancy=occupancies)
  data = []
  for line in connections:
      data.append({
          'company': line.company,
          'route': line.route.geojson,  # Hier wird die Geometrie im GeoJSON-Format abgerufen
          'occupancy': line.occupancy.occupancy,
          'date': line.occupancy.date,
      })
  # data = serialize('geojson', connections, geometry_field='route', fields=('company', 'occupancy'))
  return JsonResponse(data, safe=False)